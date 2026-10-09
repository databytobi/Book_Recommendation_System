// apps/frontend/web/components/auth/AuthHero.tsx

// FIX: Removed unused imports
import { cn } from "@/lib/utils";

interface AuthHeroProps {
  className?: string;
}

export function AuthHero({ className }: AuthHeroProps) {
  return (
    <div className={cn("max-w-md space-y-8", className)}>
      {/* Badge */}
      <div className="inline-flex items-center rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-medium text-white/90 backdrop-blur-sm">
        <span className="relative flex h-2 w-2 mr-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
        </span>
        AI Powered Book Discovery
      </div>

      {/* Main Heading */}
      <h1 className="text-4xl sm:text-5xl font-bold leading-tight tracking-tight text-white">
        Discover your next
        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-200 via-white to-violet-200">
          favorite book.
        </span>
      </h1>

      {/* Description */}
      <p className="text-base sm:text-lg text-indigo-100/90 leading-relaxed max-w-sm">
        Personalized recommendations, intelligent author discovery,
        and a reading experience built around you.
      </p>

      {/* Feature List */}
      <div className="flex flex-col gap-2 pt-2">
        <div className="flex items-center gap-3 text-sm text-indigo-100/80">
          <svg className="h-5 w-5 flex-shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {/* FIX: Replaced ' with &apos; */}
          <span>Smart recommendations powered by AI</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-indigo-100/80">
          <svg className="h-5 w-5 flex-shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Discover authors and genres you&apos;ll love</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-indigo-100/80">
          <svg className="h-5 w-5 flex-shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Track your reading journey effortlessly</span>
        </div>
      </div>

      {/* Stats Section */}
      <div className="flex items-center gap-6 pt-2 border-t border-white/10">
        <div className="text-center">
          <div className="text-2xl font-bold text-white">50K+</div>
          <div className="text-xs text-indigo-200/70">Active Readers</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-white">1M+</div>
          <div className="text-xs text-indigo-200/70">Books Discovered</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-white">4.8★</div>
          <div className="text-xs text-indigo-200/70">Average Rating</div>
        </div>
      </div>
    </div>
  );
}

// Alternative version with illustrations
export function AuthHeroWithIllustration({ className }: AuthHeroProps) {
  return (
    <div className={cn("max-w-md space-y-8", className)}>
      {/* Badge */}
      <div className="inline-flex items-center rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-medium text-white/90 backdrop-blur-sm">
        <span className="relative flex h-2 w-2 mr-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
        </span>
        AI Powered Book Discovery
      </div>

      {/* Main Heading */}
      <h1 className="text-4xl sm:text-5xl font-bold leading-tight tracking-tight text-white">
        Discover your next
        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-200 via-white to-violet-200">
          favorite book.
        </span>
      </h1>

      {/* Description */}
      <p className="text-base sm:text-lg text-indigo-100/90 leading-relaxed max-w-sm">
        Personalized recommendations, intelligent author discovery,
        and a reading experience built around you.
      </p>

      {/* Stats */}
      <div className="flex items-center gap-6 pt-2">
        <div className="text-center">
          <div className="text-2xl font-bold text-white">50K+</div>
          <div className="text-xs text-indigo-200/70">Active Readers</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-white">1M+</div>
          <div className="text-xs text-indigo-200/70">Books Discovered</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-white">4.8★</div>
          <div className="text-xs text-indigo-200/70">Average Rating</div>
        </div>
      </div>
    </div>
  );
}

// Minimal version without stats
export function AuthHeroMinimal({ className }: AuthHeroProps) {
  return (
    <div className={cn("max-w-md space-y-6", className)}>
      {/* Badge */}
      <div className="inline-flex items-center rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-medium text-white/90 backdrop-blur-sm">
        ✨ AI Powered
      </div>

      {/* Main Heading */}
      <h1 className="text-4xl sm:text-5xl font-bold leading-tight tracking-tight text-white">
        Discover your next
        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-200 via-white to-violet-200">
          favorite book.
        </span>
      </h1>

      {/* Description */}
      <p className="text-sm sm:text-base text-indigo-100/80 leading-relaxed max-w-sm">
        Personalized recommendations, intelligent author discovery,
        and a reading experience built around you.
      </p>
    </div>
  );
}