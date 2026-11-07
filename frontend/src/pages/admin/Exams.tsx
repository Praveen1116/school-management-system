import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listExams, listGradingRules, getExamResults } from '@/api/exams'
import { listSubjects } from '@/api/subjects'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import DataTable, { Column } from '@/components/DataTable'
import ErrorMessage from '@/components/ErrorMessage'
import { formatDate, extractError } from '@/utils/helpers'
import GradingRuleDialog from './GradingRuleDialog'
import type { Exam, GradingRule, Subject, ExamResult } from '@/types'

export default function Exams(): React.ReactElement {
  const [exams, setExams] = useState<Exam[]>([])
  const [rules, setRules] = useState<GradingRule[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [ruleModalOpen, setRuleModalOpen] = useState<boolean>(false)
  const [resultsModalOpen, setResultsModalOpen] = useState<boolean>(false)
  const [examResults, setExamResults] = useState<ExamResult[]>([])
  const navigate = useNavigate()

  useEffect(() => { loadData() }, [])

  async function loadData(): Promise<void> {
    try {
      setLoading(true)
      const [eRes, rRes, sRes] = await Promise.all([listExams(), listGradingRules(), listSubjects()])
      setExams(eRes.data.data || [])
      setRules(rRes.data.data || [])
      setSubjects(sRes.data.data || [])
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  const subjectMap: Record<string, string> = Object.fromEntries(subjects.map(s => [s.id, `${s.name} (${s.code})`]))

  async function viewResults(examId: string): Promise<void> {
    try {
      const res = await getExamResults(examId)
      setExamResults(res.data.data || [])
      setResultsModalOpen(true)
    } catch (err: unknown) {
      alert(extractError(err))
    }
  }

  const examColumns: Column<Exam>[] = [
    { label: 'Name', key: 'name' },
    { label: 'Subject', render: (r: Exam) => subjectMap[r.subject_id] || r.subject_name || r.subject_id },
    { label: 'Total Marks', key: 'total_marks' },
    { label: 'Exam Date', render: (r: Exam) => formatDate(r.exam_date) },
    {
      label: 'Actions',
      render: (r: Exam) => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => viewResults(r.id)}>View Results</Button>
          <Button size="sm" variant="outline" onClick={() => navigate(`/admin/exams/${r.id}/edit`)}>Edit</Button>
        </div>
      ),
    },
  ]

  const ruleColumns: Column<GradingRule>[] = [
    { label: 'Rule Set Name', key: 'name' },
    { label: 'Grade', key: 'grade_label' },
    { label: 'Min Marks', key: 'min_marks' },
    { label: 'Max Marks', key: 'max_marks' },
  ]

  const resultColumns: Column<ExamResult>[] = [
    { label: 'Student', render: (r: ExamResult) => r.student_name || r.student_id },
    { label: 'Marks', render: (r: ExamResult) => `${r.marks_obtained} / ${r.total_marks || 100}` },
    { label: 'Grade', key: 'grade' },
  ]

  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900">Exams</h1>
          <Link to="/admin/exams/new"><Button className="bg-slate-900 text-white">Add Exam</Button></Link>
        </div>
        <ErrorMessage message={error} />
        <DataTable<Exam> columns={examColumns} data={exams} loading={loading} />
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-900">Grading Rules</h2>
          <Button variant="outline" onClick={() => setRuleModalOpen(true)}>Add Rule</Button>
        </div>
        <DataTable<GradingRule> columns={ruleColumns} data={rules} loading={loading} />
      </div>

      <Dialog open={resultsModalOpen} onOpenChange={setResultsModalOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Exam Results</DialogTitle></DialogHeader>
          <DataTable<ExamResult> columns={resultColumns} data={examResults} emptyMessage="No results entered for this exam yet" />
        </DialogContent>
      </Dialog>

      <GradingRuleDialog
        open={ruleModalOpen}
        onOpenChange={setRuleModalOpen}
        onSuccess={() => loadData()}
      />
    </div>
  )
}
