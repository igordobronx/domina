import { test, expect } from "@playwright/test";

test("matemática usa escala própria e gestor não aprova", async ({ page }) => {
  await page.goto("/#aluno/atividades/a2");
  await page
    .getByRole("textbox", { name: "Texto da atividade" })
    .fill(
      "Para quatro quilômetros, a função resulta em 2 vezes 4 mais 5, totalizando treze reais.",
    );
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Enviar para revisão" }).click();
  await page.getByLabel("Perfil de demonstração").selectOption("professor");
  await page.getByRole("button", { name: /Funções no dia a dia/ }).click();
  await expect(page.getByText("/ 10 pontos")).toBeVisible();
  await page.getByLabel("Nota de raciocínio").selectOption("9");
  await page
    .getByRole("textbox", { name: "Feedback do professor" })
    .fill("Raciocínio correto. Identifique a unidade no resultado.");
  await page
    .getByRole("button", { name: "Aprovar e liberar resultado" })
    .click();
  await page.getByRole("button", { name: "Voltar à revisão" }).click();
  await expect(
    page.getByText("Correção aprovada", { exact: true }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Aprovar e liberar resultado" })
    .click();
  await page.getByRole("button", { name: "Confirmar aprovação" }).click();
  await page.goto("/#gestor/revisoes/a2");
  await page.reload();
  await expect(page.getByText("Uma visão do que importa.")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Aprovar e liberar resultado" }),
  ).toHaveCount(0);
});

test("aluno envia, professor aprova e aluno vê o resultado; rascunhos e persistência", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Enviar atividade", exact: true })
    .click();
  await page
    .getByRole("button", { name: /Os desafios da inclusão digital/ })
    .click();
  await page
    .getByRole("button", { name: "Enviar para revisão", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("40 caracteres");
  await page
    .getByRole("textbox", { name: "Texto da atividade" })
    .fill(
      "A inclusão digital depende de acesso à internet e educação. É necessário ampliar a infraestrutura nas escolas e capacitar professores para reduzir as desigualdades.",
    );
  await page.reload();
  await expect(
    page.getByRole("textbox", { name: "Texto da atividade" }),
  ).toHaveValue(/A inclusão digital/);
  await page.getByRole("checkbox").check();
  await page
    .getByRole("button", { name: "Enviar para revisão", exact: true })
    .click();
  await expect(page.getByText("Recebemos sua atividade!")).toBeVisible();
  await expect(page.getByText("740", { exact: true })).toHaveCount(0);
  await page.getByLabel("Perfil de demonstração").selectOption("professor");
  await page
    .getByRole("button", { name: /Os desafios da inclusão digital/ })
    .click();
  await page.getByLabel("Nota da competência 1").selectOption("180");
  await page
    .getByRole("textbox", { name: "Feedback do professor" })
    .fill(
      "Boa tese. Desenvolva exemplos e conecte seus argumentos à proposta de intervenção.",
    );
  await page
    .getByRole("button", { name: "Aprovar e liberar resultado" })
    .click();
  await page.getByRole("button", { name: "Confirmar aprovação" }).click();
  await expect(
    page.getByText("Correção aprovada", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("Perfil de demonstração").selectOption("aluno");
  await page
    .getByRole("button", { name: "Enviar atividade", exact: true })
    .click();
  await page
    .getByRole("button", { name: /Os desafios da inclusão digital/ })
    .click();
  await expect(
    page.getByText(
      "Boa tese. Desenvolva exemplos e conecte seus argumentos à proposta de intervenção.",
    ),
  ).toBeVisible();
  await expect(page.getByText("760", { exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByText("760", { exact: true })).toBeVisible();
});

test("prática, busca sem resultado e histórico do navegador", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Começar a praticar", exact: true })
    .click();
  await page.getByRole("radio", { name: "B Portanto" }).check();
  await page.getByRole("button", { name: "Conferir resposta" }).click();
  await expect(page.getByText("Isso mesmo. Mais um passo!")).toBeVisible();
  await page.getByRole("button", { name: "Concluir prática" }).click();
  await expect(page.getByText("Concluído", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Buscar no Domina" }).click();
  await page
    .getByRole("textbox", { name: "Buscar telas ou atividades" })
    .fill("zzzzz");
  await expect(
    page.getByText("Nenhum resultado. Tente “atividades” ou “cultura”."),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page
    .getByRole("button", { name: "Minha evolução", exact: true })
    .click();
  await expect(page.getByText("Olha o quanto você avançou.")).toBeVisible();
  await page.goBack();
  await expect(page.getByText("Seu próximo passo começa aqui.")).toBeVisible();
});

test("PWA esconde convite em standalone e permite dispensar no navegador", async ({
  browser,
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Instalar app", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Dispensar convite de instalação" })
    .click();
  await page.reload();
  await expect(
    page.getByRole("button", { name: "Instalar app", exact: true }),
  ).toHaveCount(0);
  const context = await browser.newContext();
  await context.addInitScript(() => {
    const original = window.matchMedia.bind(window);
    window.matchMedia = (query) =>
      query === "(display-mode: standalone)"
        ? Object.assign(original(query), { matches: true })
        : original(query);
  });
  const standalone = await context.newPage();
  await standalone.goto("/");
  await expect(
    standalone.getByRole("button", { name: "Instalar app", exact: true }),
  ).toHaveCount(0);
  await context.close();
});

test("PWA tem manifest válido, controla a página e recarrega offline", async ({
  page,
  context,
}) => {
  await page.goto("/");
  await page.evaluate(async () => {
    await navigator.serviceWorker.ready;
  });
  await page.reload();
  await expect
    .poll(() =>
      page.evaluate(() => Boolean(navigator.serviceWorker.controller)),
    )
    .toBe(true);
  const response = await page.request.get("/manifest.webmanifest");
  const manifest = await response.json();
  expect(manifest.display).toBe("standalone");
  expect(manifest.icons).toHaveLength(3);
  await context.setOffline(true);
  await page.reload();
  await expect(page.getByText("Bom te ver, Ana.")).toBeVisible();
  await expect(page.getByText(/Você está offline/)).toBeVisible();
});

test("responsividade e capturas para revisão visual", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/");
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({
    path: "tmp/screenshots/desktop.png",
    fullPage: true,
    animations: "disabled",
  });
  for (const width of [390, 360, 768]) {
    await page.setViewportSize({ width, height: 844 });
    await expect
      .poll(() =>
        page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      )
      .toBe(true);
    if (width === 390)
      await page.screenshot({
        path: "tmp/screenshots/mobile.png",
        fullPage: true,
        animations: "disabled",
      });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page
    .getByRole("navigation", { name: "Navegação rápida" })
    .getByRole("button", { name: "atividades", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Minhas atividades" }),
  ).toBeVisible();
  expect(errors).toEqual([]);
});
