from django.db import models
from django.utils import timezone
from smart_selects.db_fields import GroupedForeignKey
from django.core.exceptions import ObjectDoesNotExist
import sys, os, subprocess

# import global variables
sys.path.append('/Users/Alexis/Desktop/research project/jplag_v1/jplag_app')
import config


# Create your models here.
class Assignment(models.Model):
	name_assignment = models.CharField(max_length=100, unique=True, verbose_name = 'Assignment ')
	date_assignment = models.DateTimeField(default=timezone.now, verbose_name = 'Date ')
	def __str__(self):
		return self.name_assignment
	class Meta:
		unique_together = ('name_assignment',)

	# Saving Assignment : 
	# exist : rename directory
	# else : create directory corresponding to the assignment + create a submissions 	# 			folder and a textfile named student_list.txt
	def save(self, *args, **kwargs):
		try:
			this = Assignment.objects.get(id=self.id)
			subprocess.call('mv "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + this.name_assignment + '" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + self.name_assignment + '"', shell=True)

		except ObjectDoesNotExist:	
			subprocess.call('mkdir "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + self.name_assignment + '"', shell=True)
			subprocess.call('mkdir "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + self.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '"', shell=True)
			subprocess.call('echo "" > "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + self.name_assignment + '/' + config.STUDENT_LIST + '"', shell=True)
		super(Assignment, self).save(*args, **kwargs)



class Submission(models.Model):
	assignment = models.ForeignKey(Assignment, verbose_name = 'Assignment ')
	id_student_submission = models.IntegerField(verbose_name = 'Identifiant ')
	name_student_submission = models.CharField(max_length=30, verbose_name = 'Name ')
	date_submission = models.DateTimeField(default=timezone.now, verbose_name = 'Date ')

	def __str__(self):              # __unicode__ on Python 2
		return '%s' % (self.name_student_submission)
	class Meta:
		unique_together = ('assignment', 'id_student_submission',)


	# Saving Submission : 
	# exist : update submission directory and student_list.txt
	# else : create directory corresponding to the submission into the selected 		# 			assignment + add the name of student to the student_list.txt
	def save(self, *args, **kwargs):
		try:
			this = Submission.objects.get(id=self.id)
			if (this.id_student_submission != self.id_student_submission) or (this.name_student_submission != self.name_student_submission):
				subprocess.call('mv "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + this.assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + str(this.id_student_submission) + ' ' + this.name_student_submission + '" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + self.assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + str(self.id_student_submission) + ' ' + self.name_student_submission + '"', shell=True)
				subprocess.call('sed -i "' + '"' + ' "s/' + str(this.id_student_submission) + '[[:space:]]' + str(this.name_student_submission) + '/' + str(self.id_student_submission) + ' ' + str(self.name_student_submission) + '/g" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + this.assignment.name_assignment + '/' + config.STUDENT_LIST + '"', shell=True)
		
		except ObjectDoesNotExist:
			subprocess.call('mkdir "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + self.assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + str(self.id_student_submission) + ' ' + self.name_student_submission + '"', shell=True)
			subprocess.call('echo "' + str(self.id_student_submission) + ' ' + self.name_student_submission +  '" >> "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + self.assignment.name_assignment + '/' + config.STUDENT_LIST + '"', shell=True)	
		super(Submission, self).save(*args, **kwargs)


	# Deleting Submission : 
	# -> delete submission directory and student name from student_list.txt
	def delete(self, *args, **kwargs):
		this = Submission.objects.get(id=self.id)
		subprocess.call('rm -rf "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + this.assignment.name_assignment + '/' + config.SUBMISSIONS_FOLDER + '/' + str(this.id_student_submission) + ' ' + this.name_student_submission + '"', shell=True)
		subprocess.call('sed -i "' + '"' + ' "s/' + str(this.id_student_submission) + '[[:space:]]' + str(this.name_student_submission) + '/' + ' ' + '/g" "' + config.ROOT_SUBMISSIONS_FOLDER + '/' + this.assignment.name_assignment + '/' + config.STUDENT_LIST + '"', shell=True)
		super(Submission, self).delete(*args, **kwargs)



class SubmissionFile(models.Model):
	submission = models.ForeignKey(Submission, verbose_name = 'Submission ')
	
	def _get_upload_to(self, filename):
		return '%s/%s/%s %s/%s' % (self.submission.assignment.name_assignment, config.SUBMISSIONS_FOLDER, self.submission.id_student_submission, self.submission.name_student_submission, filename)

	file_submission = models.FileField(upload_to=_get_upload_to)
	
	class Meta:
		unique_together = ('submission', 'file_submission',)


	# Saving File : 
	# exist : update file
	# else : upload file
	def save(self, *args, **kwargs):
		alreadyExist = SubmissionFile.objects.filter(
        	submission__exact=self.submission
		).filter(
			file_submission__exact=self._get_upload_to(self.file_submission)
		)

		if not alreadyExist:
			try:
				this = SubmissionFile.objects.get(id=self.id)
				if this.file_submission != self.file_submission:
					this.file_submission.delete(save=False)
					super(SubmissionFile, self).save(*args, **kwargs)
			except ObjectDoesNotExist:
				super(SubmissionFile, self).save(*args, **kwargs)

	
	# Deleting File : 
	# -> delete file 
	def delete(self, *args, **kwargs):
		this = SubmissionFile.objects.get(id=self.id)
		this.file_submission.delete(save=False)
		super(SubmissionFile, self).delete(*args, **kwargs)



class Similarity(models.Model):
	assignment = models.ForeignKey(Assignment, verbose_name = 'Assignment ')
	sub1 = GroupedForeignKey(Submission, 'assignment', related_name='Student_1', verbose_name = 'Student 1 ')
	sub2 = GroupedForeignKey(Submission, 'assignment', related_name='Student_2', verbose_name = 'Student 2 ')
	similarity = models.FloatField(default=0.0, verbose_name = 'Similarity ')
	def __str__(self):              # __unicode__ on Python 2
		return '%s : %s - %s : 0.%s' % (self.assignment, self.sub1, self.sub2, self.similarity)
	class Meta:
		unique_together = ('assignment', 'sub1', 'sub2',)