"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Home, ChefHat, ShoppingBasket, MessageSquare,
  MapPin, Settings, Menu, X, Utensils, BarChart3,
} from "lucide-react";

const NAV_LINKS = [
  { href: "/",            label: "Home",                icon: Home           },
  { href: "/dish",        label: "Dish Recognition",    icon: ChefHat        },
  { href: "/ingredients", label: "Ingredients",         icon: ShoppingBasket },
  { href: "/assistant",   label: "AI Assistant",        icon: MessageSquare  },
  { href: "/places",      label: "Nearby Places",       icon: MapPin         },
  { href: "/presentation", label: "Presentation",       icon: BarChart3      },
];

interface Props {
  children: React.ReactNode;
}

export default function AppShell({ children }: Props) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  function isActive(href: string) {
    return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(href + "/");
  }

  function NavItem({ href, label, icon: Icon, onClick }: {
    href: string; label: string; icon: React.ElementType; onClick?: () => void;
  }) {
    const active = isActive(href);
    return (
      <Link
        href={href}
        onClick={onClick}
        className={[
          "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
          active
            ? "bg-orange-50 text-orange-600"
            : "text-gray-500 hover:bg-gray-50 hover:text-gray-800",
        ].join(" ")}
      >
        <Icon size={18} strokeWidth={active ? 2.5 : 1.8} />
        <span>{label}</span>
        {active && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-orange-500" />}
      </Link>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#F8F9FA]">

      {/* ── Desktop Sidebar ── */}
      <aside className="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:w-60 lg:z-40 bg-white border-r border-gray-100">
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-gray-100">
          <div className="w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-sm"
               style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}>
            <Utensils size={16} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-900 leading-tight">SmartKitchen</p>
            <p className="text-[10px] text-gray-400 leading-tight">AI Cooking Assistant</p>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {NAV_LINKS.map((link) => <NavItem key={link.href} {...link} />)}
        </nav>

        <div className="px-3 py-4 border-t border-gray-100">
          <Link
            href="/settings"
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-gray-500 hover:bg-gray-50 hover:text-gray-800"
          >
            <Settings size={18} strokeWidth={1.8} />
            <span>Settings</span>
          </Link>
        </div>
      </aside>

      {/* ── Mobile Top Bar ── */}
      <div className="lg:hidden fixed top-0 inset-x-0 z-40 h-14 bg-white border-b border-gray-100 flex items-center px-4 gap-3">
        <button onClick={() => setMobileOpen(true)} className="p-2 rounded-lg text-gray-500 hover:bg-gray-100">
          <Menu size={20} />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white"
               style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}>
            <Utensils size={14} strokeWidth={2.5} />
          </div>
          <span className="font-bold text-gray-900 text-sm">SmartKitchen</span>
        </div>
        <Link href="/settings" className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 cursor-pointer">
          <Settings size={18} />
        </Link>
      </div>

      {/* ── Mobile Drawer Overlay ── */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/40" onClick={() => setMobileOpen(false)} />
          <div className="relative flex flex-col w-64 bg-white h-full shadow-2xl">
            <div className="flex items-center justify-between px-4 py-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white"
                     style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}>
                  <Utensils size={14} strokeWidth={2.5} />
                </div>
                <span className="font-bold text-sm text-gray-900">SmartKitchen</span>
              </div>
              <button onClick={() => setMobileOpen(false)} className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100">
                <X size={18} />
              </button>
            </div>
            <nav className="flex-1 px-3 py-4 space-y-0.5">
              {NAV_LINKS.map((link) => <NavItem key={link.href} {...link} onClick={() => setMobileOpen(false)} />)}
            </nav>
          </div>
        </div>
      )}

      {/* ── Main Content ── */}
      <div className="flex-1 lg:pl-60 pb-16 lg:pb-0">
        <main className="pt-14 lg:pt-0 min-h-screen">
          {children}
        </main>
      </div>

      {/* ── Mobile Bottom Nav ── */}
      <nav className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-gray-100 flex">
        {NAV_LINKS.filter(l => l.href !== "/").map(({ href, label, icon: Icon }) => {
          const active = isActive(href);
          return (
            <Link
              key={href}
              href={href}
              className={[
                "flex-1 flex flex-col items-center gap-0.5 py-2 text-[10px] font-medium transition-colors",
                active ? "text-orange-600" : "text-gray-400",
              ].join(" ")}
            >
              <Icon size={20} strokeWidth={active ? 2.5 : 1.8} />
              <span>{label.split(" ")[0]}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
