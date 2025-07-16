import type { Route } from "./+types/home";
import { Navigation } from "../components/layout/Navigation";
import { Hero } from "../components/sections/Hero";
import { Footer } from "../components/layout/Footer";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "GuildRoster - Command Your Guild's Destiny" },
    { name: "description", content: "Track attendance, manage rosters, and lead your team to victory in Azeroth's greatest challenges with GuildRoster." },
  ];
}

export function loader({ context }: Route.LoaderArgs) {
  return { message: context.VALUE_FROM_EXPRESS };
}

export default function Home({ loaderData }: Route.ComponentProps) {
  return (
    <div className="min-h-screen bg-slate-900">
      <Navigation />
      <Hero />
      <Footer />
    </div>
  );
}
