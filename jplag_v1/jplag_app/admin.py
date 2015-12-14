from django.contrib import admin
from django import forms
from .models import Assignment, Submission, SubmissionFile, Similarity
import subprocess, os, config


def runJPlag(submission):
	# Get parameters
	assignment = submission.assignment
	id_student = submission.id_student_submission
	student = submission.name_student_submission

	# Set '~' as first character of current directory name (used for JPlag to detect new submissions)
	subprocess.call('mv "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + str(id_student) + ' ' + student + '" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/~' + str(id_student) + ' ' + student + '"', shell=True)

	# Run JPLAG
	currentDirectory = os.getcwd()
	os.chdir(r'./' + config.SUBMISSIONS_FOLDER + '/')
	pipe = subprocess.Popen(['java', '-jar', '../jplag.jar', submission.assignment.name_assignment], stdout=subprocess.PIPE, stderr=open(submission.assignment.name_assignment + "/stderr.txt","w"))
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
	subprocess.call('mv "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/~' + str(id_student) + ' ' + student + '" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + str(id_student) + ' ' + student + '"', shell=True)


# Register your models here
class AssignmentAdmin(admin.ModelAdmin):
	# Display assignment
	list_display = ('name_assignment', 'date_assignment')
	ordering = ('name_assignment',)

	# Refuse to delete assignment
	def get_actions(self, request):
		actions = super(AssignmentAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	# On top
	search_fields = ['name_assignment']

	# On right
	list_filter = ['date_assignment']
	

class SubmissionFileAdmin(admin.TabularInline):
	model = SubmissionFile
	extra = 1

	# Link of files
	def file_submission_link(self):
		if self.file_submission:
			return u'<img src="%s" />' % self.file_submission.url 
		else:
			return '(No image found)'
		file_submission_link.allow_tags = True


class SubmissionAdmin(admin.ModelAdmin):
	# Files are included in submission form
	inlines = [
		SubmissionFileAdmin,
	]

	# Add submission
	fieldsets = [
        ('Assignment', {'fields': ['assignment']}),
        ('Submission', {'fields': ('id_student_submission', 'name_student_submission', 'date_submission')}),
    ]

	# Delete submission
	def delete_selected_submissions(self, request, obj):
		for o in obj.all():
			o.delete()

	def get_actions(self, request):
		actions = super(SubmissionAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions
	actions = ['delete_selected_submissions']

	# Display submission
	list_display = ('assignment', 'id_student_submission', 'name_student_submission', 'date_submission')
	ordering = ('assignment', 'id_student_submission', 'name_student_submission', 'date_submission',)

	# On top
	search_fields = ['assignment__name_assignment']

	# On right
	list_filter = ['date_submission']

	# Saving submissions then all files and finally run JPlag
	def save_formset(self, request, form, formset, change):
		for form in formset.forms:
			form.instance.user = request.user
		formset.save()

	def response_add(self, request, new_object):
		obj = self.after_saving_model_and_related_inlines(new_object)
		return super(SubmissionAdmin, self).response_add(request, obj)

	def response_change(self, request, obj):
		obj = self.after_saving_model_and_related_inlines(obj)
		return super(SubmissionAdmin, self).response_change(request, obj)

	def after_saving_model_and_related_inlines(self, obj):
		runJPlag(obj)
		return obj


# Add manually similarity - not used
class SimilarityForm(forms.ModelForm):
	def clean(self):
		cleaned_data = super(SimilarityForm, self).clean()
		assignment = cleaned_data.get('assignment')		
		student1 = cleaned_data.get('sub1')
		student2 = cleaned_data.get('sub2')
		if (not assignment) or (not student1) or (not student2):
			raise forms.ValidationError('Missing field(s).')		

		assignment_student1 = student1.assignment
		assignment_student2 = student2.assignment
		if assignment_student1 != assignment:
			raise forms.ValidationError('Student 1 didn’t submit to %s.' % assignment.name_assignment)
		if assignment_student2 != assignment:
			raise forms.ValidationError('Student 2 didn’t submit to %s.' % assignment.name_assignment)
		if student1 == student2:
			raise forms.ValidationError('Students have to be differents.')
		return self.cleaned_data


class SimilarityAdmin(admin.ModelAdmin):
	# Add similarity - not used
	form = SimilarityForm
	fieldsets = [
        ('Assignment', {'fields': ['assignment']}),
        ('Students', {'fields': ('sub1', 'sub2')}),
		('Similarity', {'fields': ['similarity']}),
    ]
	# Refuse to add similarity
	def has_add_permission(self, request):
		return False

	# Refuse to edit similarity
	def __init__(self, *args, **kwargs):
		super(SimilarityAdmin, self).__init__(*args, **kwargs)
		self.list_display_links = (None, )

	# Refuse to delete similarity
	def get_actions(self, request):
		actions = super(SimilarityAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	# Display similarity
	list_display = ('assignment', 'sub1', 'sub2', 'similarity')
	ordering = ('assignment', 'similarity',)

	# On top
	search_fields = ['assignment__name_assignment']

	# On right
	list_filter = ['similarity']
	

admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Similarity, SimilarityAdmin)