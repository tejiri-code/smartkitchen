"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import SettingsPanel from "./SettingsPanel";

const NAV_LINKS = [
  { href: "/dish",        label: "Dish Recognition" },
  { href: "/ingredients", label: "Ingredients"       },
  { href: "/assistant",   label: "AI Assistant"      },
  { href: "/places",      label: "Nearby Places"     },
];

export default function Navbar() {
  const pathname = usePathname();
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-screen-xl mx-auto px-6 h-14 flex items-center gap-8">

        {/* Logo */}
        <Link href="/dish" className="flex items-center gap-2 shrink-0">
          <span className="text-xl">🍳</span>
          <span className="font-semibold text-gray-900 text-sm tracking-tight">SmartKitchen</span>
        </Link>

        {/* Nav tabs — underline style */}
        <nav className="flex items-stretch h-full flex-1">
          {NAV_LINKS.map(({ href, label }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={[
                  "relative px-4 flex items-center text-sm transition-colors",
                  active
                    ? "text-gray-900 font-medium"
                    : "text-gray-500 hover:text-gray-800",
                ].join(" ")}
              >
                {label}
                {active && (
                  <span
                    className="absolute bottom-0 left-0 right-0 h-0.5"
                    style={{ backgroundColor: "#FF6B35" }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Settings */}
        <div className="relative shrink-0">
          <button
            onClick={() => setSettingsOpen((v) => !v)}
            className={[
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors cursor-pointer border",
              settingsOpen
                ? "bg-gray-100 border-gray-300 text-gray-900"
                : "border-gray-200 text-gray-500 hover:bg-gray-50 hover:text-gray-800",
            ].join(" ")}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            Settings
          </button>

          {settingsOpen && <SettingsPanel onClose={() => setSettingsOpen(false)} />}
        </div>

      </div>
    </header>
  );
}
