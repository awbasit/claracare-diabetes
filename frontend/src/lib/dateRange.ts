export function toRangeStartIso(dateOnly: string): string {
  return `${dateOnly}T00:00:00.000Z`
}

export function toRangeEndIso(dateOnly: string): string {
  return `${dateOnly}T23:59:59.999Z`
}

export function isoDateDaysAgo(days: number): string {
  const date = new Date()
  date.setUTCDate(date.getUTCDate() - days)
  return date.toISOString().slice(0, 10)
}

export function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10)
}
