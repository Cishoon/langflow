import { useContext, useMemo } from "react";
import { AuthContext } from "@/contexts/authContext";

// 好看的颜色列表
const AVATAR_COLORS = [
  "#F87171", // red
  "#FB923C", // orange
  "#FBBF24", // amber
  "#A3E635", // lime
  "#34D399", // emerald
  "#22D3EE", // cyan
  "#60A5FA", // blue
  "#A78BFA", // violet
  "#F472B6", // pink
  "#E879F9", // fuchsia
];

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return Math.abs(hash);
}

export function ProfileIcon() {
  const { userData } = useContext(AuthContext);

  const username = userData?.username ?? "User";
  const initial = username.charAt(0).toUpperCase();

  const backgroundColor = useMemo(() => {
    const hash = hashString(username);
    return AVATAR_COLORS[hash % AVATAR_COLORS.length];
  }, [username]);

  return (
    <div
      className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white focus-visible:outline-0"
      style={{ backgroundColor }}
    >
      {initial}
    </div>
  );
}
