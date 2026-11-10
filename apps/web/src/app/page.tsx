const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const modules = [
  { title: "Recrutement WhatsApp", desc: "Candidatures par message ou note vocale, tri automatique par IA." },
  { title: "Planning des shifts", desc: "Affectation des agents par site et remplacements automatiques." },
  { title: "Pointage", desc: "Check-in / check-out par QR code ou géolocalisation." },
  { title: "Documents", desc: "CIN, casier, carte pro : suivi et alertes d'expiration." },
];

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-16">
      <h1 className="text-4xl font-bold tracking-tight">ShiftGuard</h1>
      <p className="mt-3 text-lg text-zinc-600 dark:text-zinc-400">
        Recrutement, planning et pointage pour les sociétés de gardiennage.
      </p>
      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        {modules.map((m) => (
          <div key={m.title} className="rounded-xl border border-zinc-200 p-5 dark:border-zinc-800">
            <h2 className="font-semibold">{m.title}</h2>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{m.desc}</p>
          </div>
        ))}
      </div>
      <p className="mt-10 text-xs text-zinc-500">API : {API_URL}</p>
    </main>
  );
}
