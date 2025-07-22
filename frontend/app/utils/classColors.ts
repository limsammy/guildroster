export function getClassColor(className: string): string {
  switch (className) {
    case "Death Knight": return "text-red-600";
    case "Warrior": return "text-yellow-900"; // Brown
    case "Druid": return "text-orange-500";
    case "Paladin": return "text-pink-400";
    case "Monk": return "text-green-400";
    case "Rogue": return "text-yellow-300";
    case "Hunter": return "text-green-800";
    case "Mage": return "text-sky-300";
    case "Warlock": return "text-purple-500";
    case "Priest": return "text-white";
    case "Shaman": return "text-blue-900";
    default: return "text-slate-200";
  }
} 