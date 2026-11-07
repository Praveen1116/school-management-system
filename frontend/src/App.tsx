import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { getDashboardPath } from '@/utils/helpers'
import Layout from '@/components/Layout'
import ProtectedRoute from '@/components/ProtectedRoute'
import Spinner from '@/components/Spinner'

import Login from '@/pages/Login'

import AdminDashboard from '@/pages/admin/Dashboard'
import AdminStudents from '@/pages/admin/Students'
import AdminStudentForm from '@/pages/admin/StudentForm'
import AdminTeachers from '@/pages/admin/Teachers'
import AdminTeacherForm from '@/pages/admin/TeacherForm'
import AdminClasses from '@/pages/admin/Classes'
import AdminSubjects from '@/pages/admin/Subjects'
import AdminAttendance from '@/pages/admin/Attendance'
import AdminExams from '@/pages/admin/Exams'
import AdminExamForm from '@/pages/admin/ExamForm'
import AdminFees from '@/pages/admin/Fees'
import AdminAuditLogs from '@/pages/admin/AuditLogs'

import TeacherDashboard from '@/pages/teacher/Dashboard'
import TeacherMyClasses from '@/pages/teacher/MyClasses'
import TeacherAttendance from '@/pages/teacher/Attendance'
import TeacherResults from '@/pages/teacher/Results'

import GuardianDashboard from '@/pages/guardian/Dashboard'
import GuardianAttendance from '@/pages/guardian/Attendance'
import GuardianResults from '@/pages/guardian/Results'
import GuardianFees from '@/pages/guardian/Fees'

function RootRedirect(): React.ReactElement {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={getDashboardPath(user.role)} replace />
}

export default function App(): React.ReactElement {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RootRedirect />} />

      {/* Admin Routes */}
      <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
        <Route element={<Layout />}>
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/students" element={<AdminStudents />} />
          <Route path="/admin/students/new" element={<AdminStudentForm />} />
          <Route path="/admin/students/:id/edit" element={<AdminStudentForm />} />
          <Route path="/admin/teachers" element={<AdminTeachers />} />
          <Route path="/admin/teachers/new" element={<AdminTeacherForm />} />
          <Route path="/admin/teachers/:id/edit" element={<AdminTeacherForm />} />
          <Route path="/admin/classes" element={<AdminClasses />} />
          <Route path="/admin/classes/new" element={<AdminClasses />} />
          <Route path="/admin/subjects" element={<AdminSubjects />} />
          <Route path="/admin/attendance" element={<AdminAttendance />} />
          <Route path="/admin/exams" element={<AdminExams />} />
          <Route path="/admin/exams/new" element={<AdminExamForm />} />
          <Route path="/admin/fees" element={<AdminFees />} />
          <Route path="/admin/audit-logs" element={<AdminAuditLogs />} />
        </Route>
      </Route>

      {/* Teacher Routes */}
      <Route element={<ProtectedRoute allowedRoles={['teacher']} />}>
        <Route element={<Layout />}>
          <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
          <Route path="/teacher/classes" element={<TeacherMyClasses />} />
          <Route path="/teacher/attendance" element={<TeacherAttendance />} />
          <Route path="/teacher/results" element={<TeacherResults />} />
        </Route>
      </Route>

      {/* Guardian Routes */}
      <Route element={<ProtectedRoute allowedRoles={['guardian']} />}>
        <Route element={<Layout />}>
          <Route path="/guardian/dashboard" element={<GuardianDashboard />} />
          <Route path="/guardian/attendance" element={<GuardianAttendance />} />
          <Route path="/guardian/results" element={<GuardianResults />} />
          <Route path="/guardian/fees" element={<GuardianFees />} />
        </Route>
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

