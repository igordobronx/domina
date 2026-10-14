import { useEffect, useState } from "react";
interface InstallEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}
export function isStandalone() {
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    Boolean((navigator as Navigator & { standalone?: boolean }).standalone)
  );
}
function wasDismissed() {
  try {
    return sessionStorage.getItem("domina.install.dismissed") === "1";
  } catch {
    return false;
  }
}
export function usePwa() {
  const [installed, setInstalled] = useState(isStandalone);
  const [dismissed, setDismissed] = useState(wasDismissed);
  const [prompt, setPrompt] = useState<InstallEvent | null>(null);
  const [offline, setOffline] = useState(!navigator.onLine);
  useEffect(() => {
    const query = window.matchMedia("(display-mode: standalone)");
    const mode = () => setInstalled(isStandalone());
    const ready = (e: Event) => {
      e.preventDefault();
      setPrompt(e as InstallEvent);
    };
    const installedNow = () => {
      setInstalled(true);
      setPrompt(null);
    };
    const online = () => setOffline(!navigator.onLine);
    query.addEventListener("change", mode);
    window.addEventListener("beforeinstallprompt", ready);
    window.addEventListener("appinstalled", installedNow);
    window.addEventListener("online", online);
    window.addEventListener("offline", online);
    return () => {
      query.removeEventListener("change", mode);
      window.removeEventListener("beforeinstallprompt", ready);
      window.removeEventListener("appinstalled", installedNow);
      window.removeEventListener("online", online);
      window.removeEventListener("offline", online);
    };
  }, []);
  const install = async () => {
    if (!prompt) return false;
    try {
      await prompt.prompt();
      const choice = await prompt.userChoice;
      if (choice.outcome === "accepted") setInstalled(true);
      return true;
    } catch {
      return false;
    } finally {
      setPrompt(null);
    }
  };
  const dismiss = () => {
    setDismissed(true);
    try {
      sessionStorage.setItem("domina.install.dismissed", "1");
    } catch {
      /* Storage may be unavailable. */
    }
  };
  return {
    showInstall: !installed && !dismissed,
    installed,
    offline,
    install,
    dismiss,
  };
}
