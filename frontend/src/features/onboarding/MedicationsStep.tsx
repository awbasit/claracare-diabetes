import { useState, type FormEvent } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import * as patientsService from "@/services/patientsService"
import type { Medication } from "@/types/patient"

interface MedicationsStepProps {
  initialMedications: Medication[]
  onBack?: () => void
  onNext?: (medications: Medication[]) => void
  onChange?: (medications: Medication[]) => void
}

const emptyForm = { name: "", dosage: "", frequency: "", time_of_day: "", purpose: "" }

export function MedicationsStep({ initialMedications, onBack, onNext, onChange }: MedicationsStepProps) {
  const [medications, setMedications] = useState<Medication[]>(initialMedications)
  const [form, setForm] = useState(emptyForm)
  const [isAdding, setIsAdding] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateMedications(next: Medication[]) {
    setMedications(next)
    onChange?.(next)
  }

  async function handleAdd(event: FormEvent) {
    event.preventDefault()
    if (!form.name.trim()) return
    setIsAdding(true)
    setError(null)
    try {
      const created = await patientsService.createMedication({
        name: form.name.trim(),
        dosage: form.dosage || null,
        frequency: form.frequency || null,
        time_of_day: form.time_of_day || null,
        purpose: form.purpose || null,
      })
      updateMedications([...medications, created])
      setForm(emptyForm)
    } catch {
      setError("Couldn't add that medication. Please try again.")
    } finally {
      setIsAdding(false)
    }
  }

  async function handleRemove(id: string) {
    setError(null)
    try {
      await patientsService.deleteMedication(id)
      updateMedications(medications.filter((medication) => medication.id !== id))
    } catch {
      setError("Couldn't remove that medication. Please try again.")
    }
  }

  return (
    <Card>
      <CardContent className="flex flex-col gap-6">
        <p className="text-sm text-muted-foreground">
          Add any medications you currently take. You can skip this step if you&apos;re not on any.
        </p>

        {medications.length > 0 && (
          <ul className="flex flex-col gap-2">
            {medications.map((medication) => (
              <li
                key={medication.id}
                className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
              >
                <div>
                  <p className="font-medium">{medication.name}</p>
                  <p className="text-muted-foreground">
                    {[medication.dosage, medication.frequency].filter(Boolean).join(" · ") ||
                      "No dosage/frequency noted"}
                  </p>
                </div>
                <Button type="button" variant="ghost" size="sm" onClick={() => handleRemove(medication.id)}>
                  Remove
                </Button>
              </li>
            ))}
          </ul>
        )}

        <form onSubmit={handleAdd} className="grid gap-3 rounded-md border p-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2">
            <Label htmlFor="med-name">Name</Label>
            <Input
              id="med-name"
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="med-dosage">Dosage</Label>
            <Input
              id="med-dosage"
              value={form.dosage}
              onChange={(event) => setForm((prev) => ({ ...prev, dosage: event.target.value }))}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="med-frequency">Frequency</Label>
            <Input
              id="med-frequency"
              placeholder="e.g. twice daily"
              value={form.frequency}
              onChange={(event) => setForm((prev) => ({ ...prev, frequency: event.target.value }))}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="med-time">Time of day</Label>
            <Input
              id="med-time"
              placeholder="e.g. morning"
              value={form.time_of_day}
              onChange={(event) => setForm((prev) => ({ ...prev, time_of_day: event.target.value }))}
            />
          </div>
          <div className="flex flex-col gap-2 sm:col-span-2">
            <Label htmlFor="med-purpose">Purpose</Label>
            <Input
              id="med-purpose"
              value={form.purpose}
              onChange={(event) => setForm((prev) => ({ ...prev, purpose: event.target.value }))}
            />
          </div>
          {error && <p className="text-sm text-destructive sm:col-span-2">{error}</p>}
          <div className="sm:col-span-2">
            <Button type="submit" variant="secondary" disabled={isAdding || !form.name.trim()}>
              {isAdding ? "Adding…" : "Add medication"}
            </Button>
          </div>
        </form>
      </CardContent>
      {(onBack || onNext) && (
        <CardFooter className="justify-between">
          {onBack ? (
            <Button type="button" variant="outline" onClick={onBack}>
              Back
            </Button>
          ) : (
            <span />
          )}
          {onNext && (
            <Button type="button" onClick={() => onNext(medications)}>
              {medications.length > 0 ? "Next" : "Skip"}
            </Button>
          )}
        </CardFooter>
      )}
    </Card>
  )
}
