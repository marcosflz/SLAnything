import { Skeleton } from "@/components/ui/progress";

/** Esqueleto genérico mientras el servidor resuelve los datos de la página. */
export function PageSkeleton({ variant = "dashboard" }: { variant?: "dashboard" | "content" | "table" }) {
  return (
    <div className="mx-auto w-full max-w-[1180px] px-4 py-8 sm:px-8" aria-busy="true" aria-live="polite">
      <span className="sr-only">Cargando… / Loading…</span>
      <Skeleton className="mb-2 h-4 w-32" />
      <Skeleton className="mb-8 h-8 w-72" />
      {variant === "dashboard" ? (
        <>
          <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-28 rounded-xl" />
            ))}
          </div>
          <div className="grid gap-6 xl:grid-cols-3">
            <Skeleton className="h-72 rounded-xl xl:col-span-2" />
            <Skeleton className="h-72 rounded-xl" />
          </div>
        </>
      ) : variant === "table" ? (
        <div className="grid gap-2">
          {Array.from({ length: 8 }).map((_, index) => (
            <Skeleton key={index} className="h-11 rounded-lg" />
          ))}
        </div>
      ) : (
        <div className="grid max-w-3xl gap-3">
          {Array.from({ length: 9 }).map((_, index) => (
            <Skeleton key={index} className={index % 4 === 3 ? "h-24" : "h-4"} />
          ))}
        </div>
      )}
    </div>
  );
}
