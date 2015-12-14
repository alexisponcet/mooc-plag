from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views import generic
from .models import Assignment, Similarity, SubmissionFile, Submission
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import timezone
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File

import json, subprocess, os, config


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'jplag/index.html'
    context_object_name = 'hasAssignment'

	# Load all assignments from the database
    def get_queryset(self):
        return Assignment.objects.order_by('name_assignment')


class verifyAndCreateNewAssignment(generic.ListView):
	def post(self, request, *args, **kwargs):
		alreadyExist = Assignment.objects.filter(
        	name_assignment__exact=request.POST.get('nameAssignment')
    	)
		result = {}

		# Create the assignment to the database
		if not alreadyExist:
			new_assignment = Assignment(name_assignment = request.POST.get('nameAssignment'))
			new_assignment.save()
			result = {"result":"creation"}
		else:
			result = {"result":"notcreation"}
		return JsonResponse(result)


def getStudentNameById(request, pk, idstudent):
	if request.method == 'GET':
		a = Assignment.objects.get(id = pk)
		alreadyExist = Submission.objects.filter(
			id_student_submission__exact=idstudent
		)
	
		# Get student name by its id when typing its
		if not alreadyExist:
			result = {"result":"notExist"}
		else:
			result = {"result":alreadyExist[0].name_student_submission}
	return JsonResponse(result)


class AssignmentView(generic.ListView):
    model = Similarity
    template_name = 'jplag/assignment.html'
    context_object_name = 'submissions_list'

	# Display all similarities concern an assignment to the user
    def get_queryset(self):
        a = Assignment.objects.get(id = self.kwargs['pk'])
		
       	return Similarity.objects.filter(
            sub1__exact=Submission.objects.filter(assignment = a)
        ).order_by('similarity')


class launchJPLAGView(generic.ListView):
	def post(self, request, *args, **kwargs):
		# Get parameters
		assignment = Assignment.objects.get(id = self.kwargs['pk'])
		id_student = request.POST.get('id_student')
		student = request.POST.get('student').replace(' ', '')
		file = request.FILES.getlist('uploadFromPC')

		alreadyExist = Submission.objects.filter(
        	assignment__exact=assignment
    	).filter(
			id_student_submission__exact=id_student
		)

		# Create the submission to the database
		if not alreadyExist:		
			new_submission = Submission(assignment=assignment, id_student_submission= id_student, name_student_submission=student)
			new_submission.save()
			
			for f in file:
				new_file = SubmissionFile(submission=new_submission, file_submission=f)
				new_file.save()			
		else:
			for f in file:
				new_file = SubmissionFile(submission=alreadyExist[0], file_submission=f)
				new_file.save()
		
		# Set '~' as first character of current directory name (used for JPlag to detect new submissions)	
		subprocess.call('mv "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + id_student + ' ' + student + '" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/~' + id_student + ' ' + student + '"', shell=True)

		# Run JPlag
		currentDirectory = os.getcwd()
		os.chdir(r'./' + config.SUBMISSIONS_FOLDER + '/')
		pipe = subprocess.Popen(['java', '-jar', '../jplag.jar', assignment.name_assignment], stdout=subprocess.PIPE, stderr=open(assignment.name_assignment + "/stderr.txt","w"))
		os.chdir(currentDirectory)

		# Get JPlag output
		i = 0
		while True:
			output = pipe.stdout.readline()
			if not output and pipe.poll() is not None:
				break
			if output:
				if not 'Comparing ' in output.decode():
					continue
				else:
					similarity = output.decode().replace('Comparing ', '')
					similarity = similarity.replace('\n', '')
					percent = similarity.split(': ')[1]
					students = similarity.split(': ')[0].split('-')
					student1 = students[0].split(' ')	
					student2 = students[1].split(' ')			
			
					if '~' in student1[0]:
						student1[0] = student1[0][1:]
					if '~' in student2[0]:
						student2[0] = student2[0][1:]
					if (student2[1] < student1[1]):
						currentStudent = student1
						student1 = student2 
						student2 = currentStudent
					#print('student_1 :' + student1[0] + '-' + student1[1])
					#print('student_2 :' + student2[0] + '-' + student2[1])
					#print('similarity :' + percent)

					sub1 = Submission.objects.filter(
        					assignment__exact=assignment
    					).filter(
							id_student_submission__exact=student1[0]
						).filter(
							name_student_submission__exact=student1[1]
						)[0]

					sub2 = Submission.objects.filter(
       					assignment__exact=assignment
    					).filter(
							id_student_submission__exact=student2[0]
						).filter(
							name_student_submission__exact=student2[1]
						)[0]

					alreadyExist = (Similarity.objects.filter(
       					assignment__exact=assignment
    				).filter(
						sub1__exact=sub1
					).filter(
						sub2__exact=sub2
					)) or  (Similarity.objects.filter(
       					assignment__exact=assignment
    				).filter(
						sub1__exact=sub2
					).filter(
						sub2__exact=sub1
					))

					if not alreadyExist:
						new_similarity = Similarity(assignment=assignment, sub1=sub1, sub2=sub2, similarity=percent)
						new_similarity.save()
					else:
						new_similarity = alreadyExist[0]
						new_similarity.similarity = percent
						new_similarity.save()	

		# Rename the current folder without the '~' character
		subprocess.call('mv "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/~' + id_student + ' ' + student + '" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + id_student + ' ' + student + '"', shell=True)
		
		a = Assignment.objects.get(id = self.kwargs['pk'])
		return HttpResponseRedirect(reverse('jplag_app:assignment',
                                    args=(self.kwargs['pk'],)))