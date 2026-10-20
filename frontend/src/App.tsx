import { useCallback, useEffect, useRef, useState } from "react";
import { useWindowDimensions } from "react-native";
import {
  BookOpen,
  ChartNoAxesCombined,
  CircleHelp,
  ClipboardCheck,
  Home,
  Layers,
  Menu,
  Search,
  Settings2,
  Sparkles,
  Users,
  X,
  WifiOff,
  Bell,
  Check,
  LogIn,
} from "lucide-react";
import type { Activity, DemoState, Page, Role } from "./types";
import { loadDemo, saveDemo } from "./services/demoStore";
import {
  ApiError,
  getToken,
  login as apiLogin,
  logout as apiLogout,
  me as apiMe,
  perfilParaRole,
  type UsuarioAtual,
} from "./services/api";
import { usePwa } from "./hooks/usePwa";
import { Badge, Button, IconButton, Logo, Modal } from "./components/ui";
import { InstallBanner } from "./components/InstallBanner";
import { Dashboard } from "./screens/Dashboard";
import { EducatorDashboard } from "./screens/EducatorDashboard";
import { allowedPages, readRoute } from "./services/navigation";
import { Activities } from "./screens/Activities";
import { Evolution, Studies } from "./screens/Learning";
import { Classes, Materials } from "./screens/Management";
import { Help, Settings } from "./screens/Settings";

const navItems: {
  id: Page;
  label: string;
  icon: typeof Home;
  roles: Role[];
}[] = [
  {
    id: "inicio",
    label: "Visão geral",
    icon: Home,
    roles: ["aluno", "professor", "gestor"],
  },
  {
    id: "atividades",
    label: "Minhas atividades",
    icon: BookOpen,
    roles: ["aluno"],
  },
  {
    id: "evolucao",
    label: "Minha evolução",
    icon: ChartNoAxesCombined,
    roles: ["aluno"],
  },
  { id: "estudos", label: "Plano de estudo", icon: Sparkles, roles: ["aluno"] },
  {
    id: "revisoes",
    label: "Revisões",
    icon: ClipboardCheck,
    roles: ["professor", "gestor"],
  },
  {
    id: "turmas",
    label: "Turmas",
    icon: Users,
    roles: ["professor", "gestor"],
  },
  {
    id: "materiais",
    label: "Materiais e critérios",
    icon: Layers,
    roles: ["professor"],
  },
];
function iniciais(nome: string): string {
  return nome.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase();
}

export function App() {
  const { width } = useWindowDimensions();
  const mobile = width <= 760;
  const [state, setState] = useState(loadDemo);
  const [initialRoute] = useState(() => readRoute(window.location.hash));
  const [role, setRole] = useState<Role>(initialRoute.role);
  const [page, setPage] = useState<Page>(initialRoute.page);
  const [activity, setActivity] = useState<string | null>(
      initialRoute.activity,
    ),
    [study, setStudy] = useState<string | null>(initialRoute.study);
  const [menu, setMenu] = useState(false),
    [toast, setToast] = useState("");
  const [modal, setModal] = useState<
    "install" | "notifications" | "search" | "login" | null
  >(null);
  const [query, setQuery] = useState("");
  const [currentUser, setCurrentUser] = useState<UsuarioAtual | null>(null);
  // enquanto nao sabemos se o token salvo ainda e valido, nao da pra decidir entre
  // mostrar a tela de login ou o app -- sem token, ja sabemos de cara (nada a checar)
  const [authChecked, setAuthChecked] = useState(() => !getToken());
  const [loginEmail, setLoginEmail] = useState("");
  const [loginSenha, setLoginSenha] = useState("");
  const [loginErro, setLoginErro] = useState("");
  const [loginCarregando, setLoginCarregando] = useState(false);
  useEffect(() => {
    if (!getToken()) return;
    apiMe()
      .then((usuario) => {
        setCurrentUser(usuario);
        setRole(perfilParaRole(usuario.perfil));
      })
      .catch(() => apiLogout())
      .finally(() => setAuthChecked(true));
  }, []);
  const [updateReady, setUpdateReady] = useState(false);
  const updateWorker = useRef<((reload?: boolean) => Promise<void>) | null>(
    null,
  );
  const pwa = usePwa();
  useEffect(() => {
    if (!mobile) setMenu(false);
  }, [mobile]);
  const previousFocus = useRef<HTMLElement | null>(null);
  const navigatingBack = useRef(false);
  useEffect(() => {
    const hash = `#${role}/${page}${activity ? `/${activity}` : study ? `/${study}` : ""}`;
    if (navigatingBack.current) {
      navigatingBack.current = false;
      return;
    }
    if (window.location.hash !== hash)
      window.history[window.location.hash ? "pushState" : "replaceState"](
        null,
        "",
        hash,
      );
  }, [role, page, activity, study]);
  useEffect(() => {
    const back = () => {
      const route = readRoute(window.location.hash);
      navigatingBack.current = true;
      setRole(route.role);
      setPage(route.page);
      setActivity(route.activity);
      setStudy(route.study);
      setMenu(false);
    };
    window.addEventListener("popstate", back);
    return () => window.removeEventListener("popstate", back);
  }, []);
  const notify = useCallback((message: string) => setToast(message), []);
  const update = useCallback(
    (fn: (s: DemoState) => DemoState) => setState(fn),
    [],
  );
  useEffect(() => {
    if (!saveDemo(state))
      setToast(
        "Leitura disponível, mas não foi possível salvar neste navegador. Exporte seus dados nas preferências.",
      );
  }, [state]);
  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(""), 6500);
    return () => clearTimeout(id);
  }, [toast]);
  useEffect(() => {
    if (import.meta.env.PROD) {
      import("virtual:pwa-register").then(({ registerSW }) => {
        updateWorker.current = registerSW({
          onNeedRefresh: () => setUpdateReady(true),
          onRegisterError: () =>
            notify(
              "O modo offline não pôde ser ativado. O site continua disponível online.",
            ),
        });
      });
    }
  }, [notify]);
  const navigate = (next: Page) => {
    setPage(allowedPages[role].includes(next) ? next : "inicio");
    setActivity(null);
    setStudy(null);
    setMenu(false);
    window.scrollTo({ top: 0, behavior: "instant" });
  };
  const openActivity = (a: Activity) => {
    if (role === "gestor") return;
    setPage(role === "aluno" ? "atividades" : "revisoes");
    setActivity(a.id);
    window.scrollTo(0, 0);
  };
  const openStudy = (id: string) => {
    setPage("estudos");
    setStudy(id);
    window.scrollTo(0, 0);
  };
  useEffect(() => {
    document.title = `Domina · ${navItems.find((n) => n.id === page)?.label || (page === "ajuda" ? "Ajuda" : "Preferências")}`;
    document.getElementById("main-content")?.focus({ preventScroll: true });
  }, [page]);
  useEffect(() => {
    if (!modal && !menu) return;
    previousFocus.current = document.activeElement as HTMLElement;
    const dialog = document.querySelector<HTMLElement>('[role="dialog"]');
    const selectors = 'button, input, select, textarea, [tabindex="0"]';
    dialog?.querySelector<HTMLElement>(selectors)?.focus();
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setModal(null);
        setMenu(false);
      }
      if (e.key === "Tab" && dialog) {
        const items = Array.from(
          dialog.querySelectorAll<HTMLElement>(selectors),
        ).filter((el) => !el.hasAttribute("disabled"));
        const first = items[0],
          last = items.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    const prior = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", handler);
    return () => {
      document.body.style.overflow = prior;
      document.removeEventListener("keydown", handler);
      previousFocus.current?.focus();
    };
  }, [modal, menu]);
  const install = async () => {
    if (!(await pwa.install())) setModal("install");
  };
  const handleLogin = async () => {
    setLoginCarregando(true);
    setLoginErro("");
    try {
      const usuario = await apiLogin(loginEmail.trim(), loginSenha);
      setCurrentUser(usuario);
      setRole(perfilParaRole(usuario.perfil));
      setLoginSenha("");
      setModal(null);
      navigate("inicio");
      notify(`Bem-vindo(a), ${usuario.nome}.`);
    } catch (erro) {
      setLoginErro(erro instanceof ApiError ? erro.message : "Não foi possível entrar. Tente de novo.");
    } finally {
      setLoginCarregando(false);
    }
  };
  const handleLogout = () => {
    apiLogout();
    setCurrentUser(null);
    setModal(null);
    notify("Você saiu da sua conta.");
  };
  const count = state.activities.filter((a) => a.status === "pendente").length;
  if (!authChecked) return <div className="login-screen" />;
  if (!currentUser)
    return (
      <div className="login-screen">
        <div className="modal login-card">
          <Logo />
          <h1>Entrar no Domina</h1>
          <p>Use o e-mail e a senha da sua escola para continuar.</p>
          <div className="form-grid">
            <label>
              Email
              <input
                type="email"
                value={loginEmail}
                autoFocus
                onChange={(e) => setLoginEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              />
            </label>
            <label>
              Senha
              <input
                type="password"
                value={loginSenha}
                onChange={(e) => setLoginSenha(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              />
            </label>
          </div>
          {loginErro && (
            <p className="tiny error" role="alert">
              {loginErro}
            </p>
          )}
          <Button
            variant="primary"
            disabled={loginCarregando || !loginEmail.trim() || !loginSenha}
            onPress={handleLogin}
          >
            {loginCarregando ? "Entrando..." : "Entrar"}
          </Button>
        </div>
      </div>
    );
  return (
    <div className="app-shell">
      <a
        className="skip-link"
        href="#main-content"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("main-content")?.focus();
        }}
      >
        Pular para o conteúdo
      </a>
      {menu && (
        <button
          className="mobile-backdrop"
          aria-label="Fechar menu"
          onClick={() => setMenu(false)}
        />
      )}
      <aside
        className={`sidebar ${menu ? "is-open" : ""}`}
        inert={mobile && !menu}
        role={mobile && menu ? "dialog" : undefined}
        aria-modal={mobile && menu ? true : undefined}
        aria-label={mobile && menu ? "Menu principal" : undefined}
      >
        <div className="sidebar-brand">
          <Logo />
          <button
            className="mobile-close"
            aria-label="Fechar menu"
            onClick={() => setMenu(false)}
          >
            <X size={23} />
          </button>
        </div>
        <div className="workspace">
          <span className="school-avatar">{currentUser.escola_nome[0] ?? "E"}</span>
          <div>
            <strong>{currentUser.escola_nome}</strong>
          </div>
        </div>
        <div className="nav-caption">SEU ESPAÇO</div>
        <nav aria-label="Navegação principal">
          {navItems
            .filter((n) => n.roles.includes(role))
            .map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                className={`nav-item ${page === id ? "selected" : ""}`}
                aria-current={page === id ? "page" : undefined}
                onClick={() => navigate(id)}
              >
                <Icon size={20} strokeWidth={1.7} />
                <span>{label}</span>
                {id === "atividades" && (
                  <span className="nav-count">
                    {
                      state.activities.filter((a) => a.status === "disponivel")
                        .length
                    }
                  </span>
                )}
                {id === "revisoes" && count > 0 && (
                  <span className="nav-count">{count}</span>
                )}
              </button>
            ))}
        </nav>
        <div className="sidebar-quote">
          <div className="quote-mark">✳</div>
          <strong>
            Do erro
            <br />
            ao domínio.
          </strong>
          <p>
            Aprender é seguir
            <br />
            em construção.
          </p>
          <div className="mini-progress">
            <span />
          </div>
        </div>
        <div className="sidebar-bottom">
          <button
            className={`nav-item ${page === "ajuda" ? "selected" : ""}`}
            onClick={() => navigate("ajuda")}
          >
            <CircleHelp size={20} />
            Central de ajuda
          </button>
          <button
            className={`nav-item ${page === "configuracoes" ? "selected" : ""}`}
            onClick={() => navigate("configuracoes")}
          >
            <Settings2 size={20} />
            Preferências
          </button>
          <div className="sidebar-profile">
            <div className="avatar">{iniciais(currentUser.nome)}</div>
            <div>
              <strong>{currentUser.nome}</strong>
              <span>
                {role === "aluno" ? "Estudante" : role === "professor" ? "Professor(a)" : "Gestor(a)"}
              </span>
            </div>
            <button aria-label="Conta" className="profile-button" onClick={() => setModal("login")}>
              <LogIn size={18} />
            </button>
          </div>
        </div>
      </aside>
      <div className="main-shell" inert={mobile && menu}>
        <header className="topbar">
          <div className="topbar-left">
            <span className="mobile-menu">
              <IconButton
                icon={Menu}
                label="Abrir menu"
                onPress={() => setMenu(true)}
              />
            </span>
            <span className="breadcrumb">
              Meu espaço <span>/</span>{" "}
              <strong>
                {navItems.find((n) => n.id === page)?.label ||
                  (page === "ajuda" ? "Ajuda" : "Preferências")}
              </strong>
            </span>
          </div>
          <div className="topbar-actions">
            <IconButton
              icon={Search}
              label="Buscar no Domina"
              onPress={() => {
                setQuery("");
                setModal("search");
              }}
            />
            <div className="notification-button">
              <IconButton
                icon={Bell}
                label="Notificações"
                onPress={() => setModal("notifications")}
              />
              <span />
            </div>
            <span className="top-avatar">{iniciais(currentUser.nome)}</span>
          </div>
        </header>
        {pwa.offline && (
          <div className="offline-bar" role="status">
            <WifiOff size={15} />
            Você está offline. Os exemplos continuam disponíveis neste aparelho.
          </div>
        )}
        {updateReady && (
          <div className="update-bar" role="status">
            Uma nova versão está pronta.
            <button onClick={() => updateWorker.current?.(true)}>
              Atualizar agora
            </button>
          </div>
        )}
        <main id="main-content" tabIndex={-1} className="main-content">
          <div key={page} className="page-transition">
            {page === "inicio" && role === "aluno" && (
              <Dashboard
                role={role}
                state={state}
                navigate={navigate}
                openActivity={openActivity}
                openStudy={openStudy}
                currentUser={currentUser}
              />
            )}
            {page === "inicio" && role !== "aluno" && (
              <EducatorDashboard
                role={role}
                state={state}
                navigate={navigate}
                openActivity={openActivity}
                currentUser={currentUser}
              />
            )}
            {(page === "atividades" || page === "revisoes") && (
              <Activities
                state={state}
                role={role}
                update={update}
                notify={notify}
                selected={activity}
                select={setActivity}
                reviewOnly={page === "revisoes"}
                currentUser={currentUser}
              />
            )}
            {page === "evolucao" && <Evolution currentUser={currentUser} />}
            {page === "estudos" && (
              <Studies
                state={state}
                update={update}
                selected={study}
                select={setStudy}
                currentUser={currentUser}
              />
            )}
            {page === "turmas" && (
              <Classes state={state} role={role} currentUser={currentUser} notify={notify} />
            )}
            {page === "materiais" && (
              <Materials state={state} update={update} notify={notify} role={role} currentUser={currentUser} />
            )}
            {page === "configuracoes" && (
              <Settings
                state={state}
                update={update}
                notify={notify}
                onInstall={() => setModal("install")}
                role={role}
                currentUser={currentUser}
              />
            )}
            {page === "ajuda" && <Help />}
            {page === "inicio" && pwa.showInstall && (
              <InstallBanner onInstall={install} onDismiss={pwa.dismiss} />
            )}
          </div>
        </main>
        <nav className="bottom-nav" aria-label="Navegação rápida">
          {navItems
            .filter((n) => n.roles.includes(role))
            .slice(0, 4)
            .map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                aria-current={page === id ? "page" : undefined}
                className={page === id ? "active" : ""}
                onClick={() => navigate(id)}
              >
                <Icon size={20} />
                <span>
                  {label
                    .replace("Minhas ", "")
                    .replace("Minha ", "")
                    .replace("Plano de estudo", "Estudar")
                    .replace("Visão geral", "Início")
                    .replace("Materiais e critérios", "Materiais")}
                </span>
              </button>
            ))}
        </nav>
      </div>
      {toast && (
        <div className="toast" role="status">
          <Check size={18} />
          <span>{toast}</span>
          <button aria-label="Fechar aviso" onClick={() => setToast("")}>
            <X size={17} />
          </button>
        </div>
      )}
      {modal && (
        <Modal
          title={
            modal === "install"
              ? "Leve o Domina com você"
              : modal === "search"
                ? "O que você procura?"
                : modal === "login"
                  ? "Sua conta"
                  : "Suas notificações"
          }
          onClose={() => setModal(null)}
        >
          {modal === "install" && (
            <>
              <p>Abra seu espaço de aprendizagem direto pela tela inicial.</p>
              {pwa.installed ? (
                <Badge>Você já está usando o aplicativo instalado.</Badge>
              ) : (
                <>
                  <ol className="install-steps">
                    <li>
                      <strong>No iPhone ou iPad</strong>
                      <p>
                        Abra o Domina no Safari, toque em Compartilhar e escolha
                        “Adicionar à Tela de Início”.
                      </p>
                    </li>
                    <li>
                      <strong>No Android</strong>
                      <p>
                        No Chrome, abra o menu ⋮ e procure “Instalar app” ou
                        “Adicionar à tela inicial”.
                      </p>
                    </li>
                    <li>
                      <strong>No computador</strong>
                      <p>
                        No Chrome ou Edge, procure o ícone de instalação na
                        barra de endereço ou a opção de instalar no menu.
                      </p>
                    </li>
                  </ol>
                  <p className="tiny muted">
                    As opções variam por navegador. Quando aberto pelo ícone
                    instalado, o convite não aparece.
                  </p>
                </>
              )}
            </>
          )}
          {modal === "notifications" && (
            <div className="notification-list">
              <div>
                <Badge>Resultado disponível</Badge>
                <h3>Uma nova oportunidade de aprender</h3>
                <p>
                  Confira as atividades aprovadas e as orientações do seu
                  professor.
                </p>
                <Button
                  onPress={() => {
                    setModal(null);
                    navigate(
                      role === "aluno"
                        ? "atividades"
                        : role === "professor"
                          ? "revisoes"
                          : "turmas",
                    );
                  }}
                >
                  Ver atividades
                </Button>
              </div>
              <div>
                <Badge tone="neutral">Seu ritmo</Badge>
                <p>
                  Seu plano tem três práticas curtas para continuar evoluindo.
                </p>
              </div>
            </div>
          )}
          {modal === "search" && (
            <>
              <label className="search-field full-search">
                <Search size={18} />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Busque telas ou atividades"
                  aria-label="Buscar telas ou atividades"
                />
              </label>
              <div className="search-results">
                {navItems
                  .filter(
                    (n) =>
                      n.roles.includes(role) &&
                      n.label.toLowerCase().includes(query.toLowerCase()),
                  )
                  .map((n) => (
                    <button
                      key={n.id}
                      onClick={() => {
                        setModal(null);
                        navigate(n.id);
                      }}
                    >
                      <n.icon size={18} />
                      {n.label}
                    </button>
                  ))}
                {state.activities
                  .filter(
                    (a) =>
                      role !== "gestor" &&
                      a.title.toLowerCase().includes(query.toLowerCase()),
                  )
                  .map((a) => (
                    <button
                      key={a.id}
                      onClick={() => {
                        setModal(null);
                        openActivity(a);
                      }}
                    >
                      <BookOpen size={18} />
                      {a.title}
                    </button>
                  ))}
                {query &&
                  !navItems.some(
                    (n) =>
                      n.roles.includes(role) &&
                      n.label.toLowerCase().includes(query.toLowerCase()),
                  ) &&
                  !state.activities.some((a) =>
                    a.title.toLowerCase().includes(query.toLowerCase()),
                  ) && (
                    <p>Nenhum resultado. Tente “atividades” ou “cultura”.</p>
                  )}
              </div>
            </>
          )}
          {modal === "login" && (
            <>
              <Logo />
              <p>
                Conectado como <strong>{currentUser.nome}</strong> ({currentUser.email}).
              </p>
              <Button variant="secondary" onPress={handleLogout}>
                Sair da conta
              </Button>
            </>
          )}
        </Modal>
      )}
    </div>
  );
}
