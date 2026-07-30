import { useState, type FormEvent } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import type { LifestyleProfileInput } from "@/types/patient"

interface LifestyleStepProps {
  initialValue: LifestyleProfileInput
  isSaving: boolean
  onSubmit: (value: LifestyleProfileInput) => void
  onBack?: () => void
  submitLabel?: string
}

export function LifestyleStep({
  initialValue,
  isSaving,
  onSubmit,
  onBack,
  submitLabel = "Next",
}: LifestyleStepProps) {
  const [sleepHoursAvg, setSleepHoursAvg] = useState(initialValue.sleep_hours_avg?.toString() ?? "")
  const [exerciseFrequency, setExerciseFrequency] = useState(initialValue.exercise_frequency ?? "")
  const [exerciseType, setExerciseType] = useState(initialValue.exercise_type ?? "")
  const [smokingStatus, setSmokingStatus] = useState(initialValue.smoking_status ?? "")
  const [alcoholUse, setAlcoholUse] = useState(initialValue.alcohol_use ?? "")
  const [stressLevel, setStressLevel] = useState(initialValue.stress_level_baseline?.toString() ?? "")
  const [mealScheduleNotes, setMealScheduleNotes] = useState(initialValue.meal_schedule_notes ?? "")

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    onSubmit({
      sleep_hours_avg: sleepHoursAvg ? Number(sleepHoursAvg) : null,
      exercise_frequency: exerciseFrequency || null,
      exercise_type: exerciseType || null,
      smoking_status: smokingStatus || null,
      alcohol_use: alcoholUse || null,
      stress_level_baseline: stressLevel ? Number(stressLevel) : null,
      meal_schedule_notes: mealScheduleNotes || null,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2">
            <Label htmlFor="sleep">Average sleep (hours/night)</Label>
            <Input
              id="sleep"
              type="number"
              step="0.5"
              min={0}
              max={24}
              value={sleepHoursAvg}
              onChange={(event) => setSleepHoursAvg(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="stress">Baseline stress level (1-10)</Label>
            <Input
              id="stress"
              type="number"
              min={1}
              max={10}
              value={stressLevel}
              onChange={(event) => setStressLevel(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="exercise-frequency">Exercise frequency</Label>
            <Input
              id="exercise-frequency"
              placeholder="e.g. 3x per week"
              value={exerciseFrequency}
              onChange={(event) => setExerciseFrequency(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="exercise-type">Exercise type</Label>
            <Input
              id="exercise-type"
              placeholder="e.g. walking, football"
              value={exerciseType}
              onChange={(event) => setExerciseType(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="smoking">Smoking status</Label>
            <Select id="smoking" value={smokingStatus} onChange={(event) => setSmokingStatus(event.target.value)}>
              <option value="">Prefer not to say</option>
              <option value="never">Never</option>
              <option value="former">Former</option>
              <option value="current">Current</option>
            </Select>
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="alcohol">Alcohol use</Label>
            <Select id="alcohol" value={alcoholUse} onChange={(event) => setAlcoholUse(event.target.value)}>
              <option value="">Prefer not to say</option>
              <option value="none">None</option>
              <option value="occasional">Occasional</option>
              <option value="moderate">Moderate</option>
              <option value="heavy">Heavy</option>
            </Select>
          </div>
          <div className="flex flex-col gap-2 sm:col-span-2">
            <Label htmlFor="meal-schedule">Meal schedule notes</Label>
            <Textarea
              id="meal-schedule"
              value={mealScheduleNotes}
              onChange={(event) => setMealScheduleNotes(event.target.value)}
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
