# Copyright (c) 2021, FOSS United and Contributors
# See license.txt

import frappe

from lms.lms.api import get_lesson_completion_stats
from lms.lms.test_helpers import BaseTestUtils


class TestLessonCompletionStats(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self._create_user("frappe@example.com", "Frappe", "Admin", ["Moderator", "Course Creator"])
		self.course = self._create_course(f"Test Course {frappe.generate_hash()}")
		self.chapter = self._create_chapter(f"Test Chapter {frappe.generate_hash()}", self.course.name)
		self.lesson = self._create_lesson(
			f"Test Lesson {frappe.generate_hash()}", self.chapter.name, self.course.name
		)
		self._create_lesson_reference(self.chapter.name, self.lesson.name)
		self._create_chapter_reference(self.course.name, self.chapter.name)

	def _create_student(self):
		email = f"student_{frappe.generate_hash()}@example.com"
		self._create_user(email, "Test", "Student", ["LMS Student"])
		return email

	def test_completion_count_ignores_unenrolled_members(self):
		enrolled = self._create_student()
		leaver = self._create_student()
		self._create_enrollment(enrolled, self.course.name)
		leaver_enrollment = self._create_enrollment(leaver, self.course.name)

		for member in (enrolled, leaver):
			self._create_lesson_progress(member, self.course.name, self.lesson.name)

		# Progress rows survive the enrollment; counting them left the lesson credited
		# to more members than the course had enrolled.
		frappe.delete_doc("LMS Enrollment", leaver_enrollment.name)
		self.cleanup_items.remove(("LMS Enrollment", leaver_enrollment.name))

		stats = get_lesson_completion_stats(self.course.name)
		self.assertEqual(len(stats), 1)
		self.assertEqual(stats[0].completion_count, 1)

		enrollments = frappe.db.get_value("LMS Course", self.course.name, "enrollments")
		self.assertLessEqual(stats[0].completion_count, enrollments)
