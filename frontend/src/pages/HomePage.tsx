import { Button } from "@/components/ui/button"

export function HomePage() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold">DiaWise AI</h1>
      <p className="text-muted-foreground">Frontend scaffold is wired up.</p>
      <Button>Get started</Button>
    </div>
  )
}
