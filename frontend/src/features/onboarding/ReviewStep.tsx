import { useState, type FormEvent, type ReactNode } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import type { OnboardingData } from "@/features/onboarding/OnboardingWizard"

interface ReviewStepProps {
  data: OnboardingData
  isSaving: boolean
  onBack: () => void
  onSubmit: (notes: string) => void
}

function SummaryRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex justify-between border-b py-1.5 text-sm last:border-none">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value === null || value === undefined || value === "" ? "—" : value}</span>
    </div>
  )
}

export function ReviewStep({ data, isSaving, onBack, onSubmit }: ReviewStepProps) {
  const [notes, setNotes] = useState("")

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    onSubmit(notes)
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardContent className="flex flex-col gap-6">
          <section>
            <h2 className="mb-1 text-sm font-semibold">Demographics</h2>
            <SummaryRow label="Age" value={data.demographics.age} />
            <SummaryRow label="Sex" value={data.demographics.sex} />
            <SummaryRow label="Height (cm)" value={data.demographics.height_cm} />
            <SummaryRow label="Weight (kg)" value={data.demographics.weight_kg} />
            <SummaryRow label="Occupation" value={data.demographics.occupation} />
          </section>

          <section>
            <h2 className="mb-1 text-sm font-semibold">Medical history</h2>
            <SummaryRow label="Diabetes type" value={data.medicalHistory.diabetes_type} />
            <SummaryRow label="Years since diagnosis" value={data.medicalHistory.years_since_diagnosis} />
            <SummaryRow label="Family history" value={data.medicalHistory.family_history ? "Yes" : "No"} />
            <SummaryRow label="Other conditions" value={data.medicalHistory.comorbidities?.join(", ")} />
          </section>

          <section>
            <h2 className="mb-1 text-sm font-semibold">Medications</h2>
            {data.medications.length === 0 ? (
              <p className="text-sm text-muted-foreground">None added.</p>
            ) : (
              <ul className="list-inside list-disc text-sm">
                {data.medications.map((medication) => (
                  <li key={medication.id}>{medication.name}</li>
                ))}
              </ul>
            )}
          </section>

          <section>
            <h2 className="mb-1 text-sm font-semibold">Lifestyle</h2>
            <SummaryRow label="Sleep (hours/night)" value={data.lifestyle.sleep_hours_avg} />
            <SummaryRow label="Exercise frequency" value={data.lifestyle.exercise_frequency} />
            <SummaryRow label="Baseline stress level" value={data.lifestyle.stress_level_baseline} />
          </section>

          <div className="flex flex-col gap-2">
            <Label htmlFor="baseline-notes">Anything else you&apos;d like your care team to know?</Label>
            <Textarea id="baseline-notes" value={notes} onChange={(event) => setNotes(event.target.value)} />
          </div>
        </CardContent>
        <CardFooter className="justify-between">
          <Button type="button" variant="outline" onClick={onBack}>
            Back
          </Button>
          <Button type="submit" disabled={isSaving}>
            {isSaving ? "Submitting…" : "Submit"}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
