import { Download, X, Smartphone } from "lucide-react";
import { Button, IconButton } from "./ui";
export function InstallBanner({
  onInstall,
  onDismiss,
}: {
  onInstall: () => void;
  onDismiss: () => void;
}) {
  return (
    <aside className="install-banner">
      <div className="install-icon">
        <Smartphone size={22} />
      </div>
      <div className="install-copy">
        <strong>Seu próximo passo, a um toque.</strong>
        <span>Adicione o Domina à tela inicial e estude no seu ritmo.</span>
      </div>
      <Button variant="secondary" small icon={Download} onPress={onInstall}>
        Instalar app
      </Button>
      <IconButton
        icon={X}
        label="Dispensar convite de instalação"
        onPress={onDismiss}
      />
    </aside>
  );
}
