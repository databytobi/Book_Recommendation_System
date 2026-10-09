// apps/frontend/web/components/auth/SocialLoginButtons.tsx

"use client";

interface SocialLoginButtonsProps {
  onGoogleClick?: () => void;
  onGitHubClick?: () => void;
  onAppleClick?: () => void;
}

export function SocialLoginButtons({
  onGoogleClick,
  onGitHubClick,
  onAppleClick,
}: SocialLoginButtonsProps) {
  const handleGoogle = () => {
    if (onGoogleClick) {
      onGoogleClick();
    } else {
      // TODO: Implement Google OAuth
      console.log("Google login clicked");
    }
  };

  const handleGitHub = () => {
    if (onGitHubClick) {
      onGitHubClick();
    } else {
      // TODO: Implement GitHub OAuth
      console.log("GitHub login clicked");
    }
  };

  const handleApple = () => {
    if (onAppleClick) {
      onAppleClick();
    } else {
      // TODO: Implement Apple OAuth
      console.log("Apple login clicked");
    }
  };

  return (
    <div className="grid grid-cols-3 gap-3">
      <button
        type="button"
        onClick={handleGoogle}
        className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
      >
        <span className="mr-2">G</span>
        Google
      </button>
      <button
        type="button"
        onClick={handleGitHub}
        className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
      >
        <span className="mr-2">🐙</span>
        GitHub
      </button>
      <button
        type="button"
        onClick={handleApple}
        className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
      >
        <span className="mr-2">🍎</span>
        Apple
      </button>
    </div>
  );
}