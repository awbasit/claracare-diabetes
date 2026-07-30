import { useState, type FormEvent } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import type { DiabetesType, MedicalHistoryInput } from "@/types/patient"

const COMMON_COMORBIDITIES = [
  { value: "hypertension", label: "Hypertension" },
  { value: "heart_disease", label: "Heart disease" },
  { value: "fatty_liver", label: "Fatty liver" },
  { value: "depression", label: "Depression" },
  { value: "anxiety", label: "Anxiety" },
]

interface MedicalHistoryStepProps {
  initialValue: MedicalHistoryInput
  isSaving: boolean
  onSubmit: (value: MedicalHistoryInput) => void
  onBack?: () => void
  submitLabel?: string
}

export function MedicalHistoryStep({
  initialValue,
  isSaving,
  onSubmit,
  onBack,
  submitLabel = "Next",
}: MedicalHistoryStepProps) {
  const [diabetesType, setDiabetesType] = useState<DiabetesType | "">(initialValue.diabetes_type ?? "")
  const [yearsSinceDiagnosis, setYearsSinceDiagnosis] = useState(
    initialValue.years_since_diagnosis?.toString() ?? ""
  )
  const [familyHistory, setFamilyHistory] = useState(initialValue.family_history ?? false)
  const [familyHistoryNotes, setFamilyHistoryNotes] = useState(initialValue.family_history_notes ?? "")
  const [latestHba1c, setLatestHba1c] = useState(initialValue.latest_hba1c?.toString() ?? "")
  const [systolic, setSystolic] = useState(initialValue.latest_blood_pressure_systolic?.toString() ?? "")
  const [diastolic, setDiastolic] = useState(initialValue.latest_blood_pressure_diastolic?.toString() ?? "")
  const [cholesterol, setCholesterol] = useState(initialValue.latest_cholesterol?.toString() ?? "")
  const [hasKidneyDisease, setHasKidneyDisease] = useState(initialValue.has_kidney_disease ?? false)
  const [hasEyeDisease, setHasEyeDisease] = useState(initialValue.has_eye_disease ?? false)
  const [hasNeuropathy, setHasNeuropathy] = useState(initialValue.has_neuropathy ?? false)
  const [comorbidities, setComorbidities] = useState<string[]>(initialValue.comorbidities ?? [])
  const [otherComorbidity, setOtherComorbidity] = useState("")

  function toggleComorbidity(value: string, checked: boolean) {
    setComorbidities((prev) => (checked ? [...prev, value] : prev.filter((item) => item !== value)))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const finalComorbidities = otherComorbidity.trim()
      ? [...comorbidities, otherComorbidity.trim()]
      : comorbidities

    onSubmit({
      diabetes_type: diabetesType || null,
      years_since_diagnosis: yearsSinceDiagnosis ? Number(yearsSinceDiagnosis) : null,
      family_history: familyHistory,
      family_history_notes: familyHistoryNotes || null,
      latest_hba1c: latestHba1c ? Number(latestHba1c) : null,
      latest_blood_pressure_systolic: systolic ? Number(systolic) : null,
      latest_blood_pressure_diastolic: diastolic ? Number(diastolic) : null,
      latest_cholesterol: cholesterol ? Number(cholesterol) : null,
      has_kidney_disease: hasKidneyDisease,
      has_eye_disease: hasEyeDisease,
      has_neuropathy: hasNeuropathy,
      comorbidities: finalComorbidities,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardContent className="flex flex-col gap-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="diabetes-type">Diabetes type</Label>
              <Select
                id="diabetes-type"
                value={diabetesType}
                onChange={(event) => setDiabetesType(event.target.value as DiabetesType | "")}
              >
                <option value="">Not sure / not applicable</option>
                <option value="type1">Type 1</option>
                <option value="type2">Type 2</option>
                <option value="gestational">Gestational</option>
                <option value="prediabetes">Prediabetes</option>
                <option value="other">Other</option>
              </Select>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="years-since-diagnosis">Years since diagnosis</Label>
              <Input
                id="years-since-diagnosis"
                type="number"
                min={0}
                value={yearsSinceDiagnosis}
                onChange={(event) => setYearsSinceDiagnosis(event.target.value)}
              />
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <Checkbox id="family-history" checked={familyHistory} onCheckedChange={setFamilyHistory} />
              <Label htmlFor="family-history" className="font-normal">
                Family history of diabetes
              </Label>
            </div>
            {familyHistory && (
              <Textarea
                placeholder="Optional notes about family history"
                value={familyHistoryNotes}
                onChange={(event) => setFamilyHistoryNotes(event.target.value)}
              />
            )}
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="flex flex-col gap-2">
              <Label htmlFor="hba1c">Latest HbA1c (%)</Label>
              <Input
                id="hba1c"
                type="number"
                step="0.1"
                value={latestHba1c}
                onChange={(event) => setLatestHba1c(event.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="systolic">Blood pressure — systolic</Label>
              <Input id="systolic" type="number" value={systolic} onChange={(event) => setSystolic(event.target.value)} />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="diastolic">Blood pressure — diastolic</Label>
              <Input
                id="diastolic"
                type="number"
                value={diastolic}
                onChange={(event) => setDiastolic(event.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2 sm:col-span-3">
              <Label htmlFor="cholesterol">Latest cholesterol</Label>
              <Input
                id="cholesterol"
                type="number"
                step="0.1"
                value={cholesterol}
                onChange={(event) => setCholesterol(event.target.value)}
              />
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <Label>Known complications</Label>
            <div className="flex items-center gap-2">
              <Checkbox id="kidney" checked={hasKidneyDisease} onCheckedChange={setHasKidneyDisease} />
              <Label htmlFor="kidney" className="font-normal">
                Kidney disease
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox id="eye" checked={hasEyeDisease} onCheckedChange={setHasEyeDisease} />
              <Label htmlFor="eye" className="font-normal">
                Eye disease
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox id="neuropathy" checked={hasNeuropathy} onCheckedChange={setHasNeuropathy} />
              <Label htmlFor="neuropathy" className="font-normal">
                Neuropathy
              </Label>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <Label>Other conditions</Label>
            <div className="grid gap-2 sm:grid-cols-2">
              {COMMON_COMORBIDITIES.map((item) => (
                <div key={item.value} className="flex items-center gap-2">
                  <Checkbox
                    id={`comorbidity-${item.value}`}
                    checked={comorbidities.includes(item.value)}
                    onCheckedChange={(checked) => toggleComorbidity(item.value, checked)}
                  />
                  <Label htmlFor={`comorbidity-${item.value}`} className="font-normal">
                    {item.label}
                  </Label>
                </div>
              ))}
            </div>
            <Input
              placeholder="Other condition (optional)"
              value={otherComorbidity}
              onChange={(event) => setOtherComorbidity(event.target.value)}
            />
          </div>
        </CardContent>
        <CardFooter className="justify-between">
          {onBack ? (
            <Button type="button" variant="outline" onClick={onBack}>
              Back
            </Button>
          ) : (
            <span />
          )}
          <Button type="submit" disabled={isSaving}>
            {isSaving ? "Saving…" : submitLabel}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
