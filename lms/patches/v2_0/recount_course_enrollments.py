from lms.lms.doctype.lms_course.lms_course import update_course_statistics


def execute():
	"""Recount enrollments now that course statistics no longer filter on member_type.

	Enrollments created before member_type gained its "Student" default sit blank and
	were dropped from the old count, so those courses have been under-reporting their
	enrolled students for as long as the rows have existed.
	"""
	update_course_statistics()
