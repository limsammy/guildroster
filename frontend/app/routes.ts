import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("login", "routes/login.tsx"),
  route("dashboard", "routes/dashboard.tsx"),
  route("members", "routes/members.tsx"),
  route("members/:id", "routes/member.tsx"),
  route("guilds", "routes/guilds.tsx"),
  route("scenarios", "routes/scenarios.tsx"),
  route("settings", "routes/settings.tsx"),
  route("teams", "routes/teams.tsx"),
  route("toons", "routes/toons.tsx"),
  route("raids", "routes/raids.tsx")
] satisfies RouteConfig;
