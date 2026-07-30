import { useState, type FormEvent } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import type { PatientUpdateInput, Sex } from "@/types/patient"

interface DemographicsStepProps {
  initialValue: PatientUpdateInput
  isSaving: boolean
  onSubmit: (value: PatientUpdateInput) => void
  submitLabel?: string
}

export function DemographicsStep({
  initialValue,
  isSaving,
  onSubmit,
  submitLabel = "Next",
}: DemographicsStepProps) {
  const [age, setAge] = useState(initialValue.age?.toString() ?? "")
  const [sex, setSex] = useState<Sex | "">(initialValue.sex ?? "")
  const [heightCm, setHeightCm] = useState(initialValue.height_cm?.toString() ?? "")
  const [weightKg, setWeightKg] = useState(initialValue.weight_kg?.toString() ?? "")
  const [occupation, setOccupation] = useState(initialValue.occupation ?? "")
  const [workSchedule, setWorkSchedule] = useState(initialValue.work_schedule ?? "")

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    onSubmit({
      age: age ? Number(age) : null,
      sex: sex || null,
      height_cm: heightCm ? Number(heightCm) : null,
      weight_kg: weightKg ? Number(weightKg) : null,
      occupation: occupation || null,
      work_schedule: workSchedule || null,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2">
            <Label htmlFor="age">Age</Label>
            <Input
              id="age"
              type="number"
              min={0}
              max={120}
              value={age}
              onChange={(event) => setAge(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="sex">Sex</Label>
            <Select id="sex" value={sex} onChange={(event) => setSex(event.target.value as Sex | "")}>
              <option value="">Prefer not to say</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </Select>
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="height">Height (cm)</Label>
            <Input
              id="height"
              type="number"
              min={0}
              step="0.1"
              value={heightCm}
              onChange={(event) => setHeightCm(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="weight">Weight (kg)</Label>
            <Input
              id="weight"
              type="number"
              min={0}
              step="0.1"
              value={weightKg}
              onChange={(event) => setWeightKg(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2 sm:col-span-2">
            <Label htmlFor="occupation">Occupation</Label>
            <Input id="occupation" value={occupation} onChange={(event) => setOccupation(event.target.value)} />
          </div>
          <div className="flex flex-col gap-2 sm:col-span-2">
            <Label htmlFor="work-schedule">Work schedule</Label>
            <Input
              id="work-schedule"
              placeholder="e.g. rotating shifts, 9-5 weekdays"
              value={workSchedule}
              onChange={(event) => setWorkSchedule(event.target.value)}
            />
          </div>
        </CardContent>
        <CardFooter className="justify-end">
          <Button type="submit" disabled={isSaving}>
            {isSaving ? "Saving…" : submitLabel}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
