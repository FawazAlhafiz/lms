# Copyright (c) 2021, FOSS United and Contributors
# See license.txt

import frappe

from lms.lms.doctype.lms_course.lms_course import get_enrollment_count
from lms.lms.test_helpers import BaseTestUtils


class TestCourseEnrollmentCount(BaseTestUtils):
	"""LMS Course.enrollments is the denominator behind every rate on the course
	dashboard, so it has to stay live and count the same population its numerators do.
	"""

	def setUp(self):
		super().setUp()
		self._create_user("frappe@example.com", "Frappe", "Admin", ["Moderator", "Course Creator"])
		self.course = self._create_course(f"Test Course {frappe.generate_hash()}")

	def _create_student(self):
		email = f"student_{frappe.generate_hash()}@example.com"
		self._create_user(email, "Test", "Student", ["LMS Student"])
		return email

	def _enrollment_count(self):
		return frappe.db.get_value("LMS Course", self.course.name, "enrollments")

	def test_count_updates_when_a_student_enrolls(self):
		self.assertEqual(self._enrollment_count(), 0)

		self._create_enrollment(self._create_student(), self.course.name)
		self.assertEqual(self._enrollment_count(), 1)

		self._create_enrollment(self._create_student(), self.course.name)
		self.assertEqual(self._enrollment_count(), 2)

	def test_count_updates_when_an_enrollment_is_removed(self):
		enrollment = self._create_enrollment(self._create_student(), self.course.name)
		self.assertEqual(self._enrollment_count(), 1)

		frappe.delete_doc("LMS Enrollment", enrollment.name)
		self.cleanup_items.remove(("LMS Enrollment", enrollment.name))

		self.assertEqual(self._enrollment_count(), 0)

	def test_enrollments_with_a_blank_member_type_are_counted(self):
		"""Nothing in the app sets member_type, so rows predating its "Student" default
		sit blank. Filtering on it dropped them and under-reported enrolled students."""
		enrollment = self._create_enrollment(self._create_student(), self.course.name)
		frappe.db.set_value("LMS Enrollment", enrollment.name, "member_type", "")

		self.assertEqual(get_enrollment_count(self.course.name), 1)
