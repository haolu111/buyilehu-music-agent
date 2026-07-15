import {
  Box,
  Button,
  Callout,
  Card,
  Flex,
  Heading,
  Separator,
  Strong,
  Tabs,
  Text,
  TextField
} from "@radix-ui/themes";
import {
  ArrowRight,
  Eye,
  EyeOff,
  KeyRound,
  LoaderCircle,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from "lucide-react";
import { FormEvent, MouseEvent, ReactNode, useCallback, useEffect, useMemo, useState } from "react";

type AuthView = "login" | "register" | "forgot";
type AuthStatus = "idle" | "checking" | "submitting" | "success" | "error";

type PublicUser = {
  email: string;
};

type AuthResponse = {
  authenticated?: boolean;
  user?: PublicUser;
  message?: string;
  error?: string;
  detail?: string;
};

const viewTitles: Record<AuthView, string> = {
  login: "欢迎回来",
  register: "创建教师账号",
  forgot: "重设密码"
};

const viewSubtitles: Record<AuthView, string> = {
  login: "登录后继续生成、管理和精修你的音乐课堂游戏。",
  register: "使用邮箱验证码创建账号，作品会保存在你的个人空间。",
  forgot: "用邮箱验证码设置新密码，然后直接回到工作台。"
};

const messageFromQuery: Record<string, string> = {
  "logged-out": "已退出登录。",
  "auth-required": "请先登录账号。"
};

export function AuthApp() {
  const [activeView, setActiveView] = useState<AuthView>("login");
  const [status, setStatus] = useState<AuthStatus>("checking");
  const [message, setMessage] = useState("正在检查登录状态。");
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [newPasswordVisible, setNewPasswordVisible] = useState(false);
  const [forgotPasswordVisible, setForgotPasswordVisible] = useState(false);
  const [registerCooldown, setRegisterCooldown] = useState(0);
  const [forgotCooldown, setForgotCooldown] = useState(0);

  const nextPath = useMemo(() => safeNextPath(new URLSearchParams(window.location.search).get("next")), []);

  const redirectToNext = useCallback(() => {
    window.location.assign(nextPath);
  }, [nextPath]);

  useEffect(() => {
    let cancelled = false;
    const params = new URLSearchParams(window.location.search);
    const queryMessage = messageFromQuery[params.get("message") || ""];

    async function checkSession() {
      try {
        const response = await fetch("/api/auth/me", { credentials: "same-origin" });
        const data = (await response.json().catch(() => ({}))) as AuthResponse;
        if (cancelled) return;
        if (response.ok && data.authenticated && data.user) {
          setStatus("success");
          setMessage("已登录，正在打开工作台。");
          window.setTimeout(redirectToNext, 240);
          return;
        }
      } catch {
        if (cancelled) return;
      }
      setStatus(queryMessage ? "success" : "idle");
      setMessage(queryMessage || "请输入邮箱和密码登录。");
    }

    checkSession();
    return () => {
      cancelled = true;
    };
  }, [redirectToNext]);

  useEffect(() => {
    if (registerCooldown <= 0) return;
    const timer = window.setTimeout(() => setRegisterCooldown((value) => Math.max(0, value - 1)), 1000);
    return () => window.clearTimeout(timer);
  }, [registerCooldown]);

  useEffect(() => {
    if (forgotCooldown <= 0) return;
    const timer = window.setTimeout(() => setForgotCooldown((value) => Math.max(0, value - 1)), 1000);
    return () => window.clearTimeout(timer);
  }, [forgotCooldown]);

  const submitAuth = async (event: FormEvent<HTMLFormElement>, url: string, successMessage: string) => {
    event.preventDefault();
    const form = event.currentTarget;
    setStatus("submitting");
    setMessage("正在提交，请稍候。");
    try {
      await postForm(url, formDataFromForm(form));
      setStatus("success");
      setMessage(successMessage);
      window.setTimeout(redirectToNext, 360);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "账号操作失败。");
    }
  };

  const requestCode = async (event: MouseEvent<HTMLButtonElement>, url: string, emailField: string, kind: "register" | "forgot") => {
    event.preventDefault();
    const form = event.currentTarget.closest("form");
    if (!form) return;
    const email = String(new FormData(form).get(emailField) || "").trim();
    if (!email) {
      setStatus("error");
      setMessage("请先填写邮箱地址。");
      return;
    }
    setStatus("submitting");
    setMessage("正在发送验证码。");
    try {
      await postForm(url, { email });
      if (kind === "register") setRegisterCooldown(60);
      if (kind === "forgot") setForgotCooldown(60);
      setStatus("success");
      setMessage("验证码已发送，请查看邮箱。");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "验证码发送失败。");
    }
  };

  const checking = status === "checking";
  const busy = status === "checking" || status === "submitting";

  return (
    <main className="auth-page">
      <header className="auth-school-mark" aria-label="华东师范大学">
        <img src="/static/assets/ecnu-logo.png" alt="华东师范大学" />
      </header>

      <section className="auth-brand-panel" aria-label="产品介绍">
        <img className="auth-agent-logo" src="/static/assets/buyilehu-logo-transparent.png" alt="不亦乐乎" />
        <Heading as="h1" className="auth-agent-title">
          音乐课堂游戏生成智能体
        </Heading>
      </section>

      <section className="auth-form-panel" aria-label="账号操作">
        <Card className="auth-card" size="4">
          <Flex direction="column" gap="5">
            <Box>
              <Heading as="h2" size="7">
                {viewTitles[activeView]}
              </Heading>
              <Text as="p" size="2" className="form-subtitle">
                <Strong>{viewSubtitles[activeView]}</Strong>
              </Text>
            </Box>

            <Tabs.Root value={activeView} onValueChange={(value) => setActiveView(value as AuthView)}>
              <Tabs.List aria-label="账号操作">
                <Tabs.Trigger value="login">登录</Tabs.Trigger>
                <Tabs.Trigger value="register">注册</Tabs.Trigger>
                <Tabs.Trigger value="forgot">忘记密码</Tabs.Trigger>
              </Tabs.List>

              <Separator size="4" />

              <Tabs.Content value="login">
                <form
                  className="auth-form"
                  onSubmit={(event) => submitAuth(event, "/api/auth/login", "登录成功，正在打开工作台。")}
                >
                  <Field label="邮箱账号" icon={<Mail size={17} />}>
                    <TextField.Root name="email" type="email" autoComplete="email" required placeholder="teacher@example.com" />
                  </Field>
                  <Field label="密码" icon={<LockKeyhole size={17} />}>
                    <PasswordField
                      name="password"
                      autoComplete="current-password"
                      visible={passwordVisible}
                      onToggle={() => setPasswordVisible((value) => !value)}
                    />
                  </Field>
                  <SubmitButton busy={busy} label="登录" />
                </form>
              </Tabs.Content>

              <Tabs.Content value="register">
                <form
                  className="auth-form"
                  onSubmit={(event) => submitAuth(event, "/api/auth/register/complete", "注册成功，正在打开工作台。")}
                >
                  <Field label="邮箱账号" icon={<Mail size={17} />}>
                    <TextField.Root name="email" type="email" autoComplete="email" required placeholder="teacher@example.com" />
                  </Field>
                  <Button
                    className="secondary-auth-action"
                    type="button"
                    variant="soft"
                    color="teal"
                    disabled={busy || registerCooldown > 0}
                    onClick={(event) => requestCode(event, "/api/auth/register/request-code", "email", "register")}
                  >
                    {registerCooldown > 0 ? `${registerCooldown} 秒后重发` : "发送邮箱验证码"}
                  </Button>
                  <Field label="邮箱验证码" icon={<KeyRound size={17} />}>
                    <TextField.Root name="code" inputMode="numeric" autoComplete="one-time-code" maxLength={6} required placeholder="6 位验证码" />
                  </Field>
                  <Field label="设置密码" icon={<LockKeyhole size={17} />}>
                    <PasswordField
                      name="password"
                      autoComplete="new-password"
                      minLength={8}
                      visible={newPasswordVisible}
                      onToggle={() => setNewPasswordVisible((value) => !value)}
                    />
                  </Field>
                  <Field label="确认密码" icon={<LockKeyhole size={17} />}>
                    <TextField.Root name="confirm_password" type="password" autoComplete="new-password" minLength={8} required />
                  </Field>
                  <SubmitButton busy={busy} label="完成注册并登录" />
                </form>
              </Tabs.Content>

              <Tabs.Content value="forgot">
                <form
                  className="auth-form"
                  onSubmit={(event) => submitAuth(event, "/api/auth/password/reset", "密码已重置，正在打开工作台。")}
                >
                  <Field label="邮箱账号" icon={<Mail size={17} />}>
                    <TextField.Root name="email" type="email" autoComplete="email" required placeholder="teacher@example.com" />
                  </Field>
                  <Button
                    className="secondary-auth-action"
                    type="button"
                    variant="soft"
                    color="teal"
                    disabled={busy || forgotCooldown > 0}
                    onClick={(event) => requestCode(event, "/api/auth/password/request-reset", "email", "forgot")}
                  >
                    {forgotCooldown > 0 ? `${forgotCooldown} 秒后重发` : "发送重置验证码"}
                  </Button>
                  <Field label="邮箱验证码" icon={<KeyRound size={17} />}>
                    <TextField.Root name="code" inputMode="numeric" autoComplete="one-time-code" maxLength={6} required placeholder="6 位验证码" />
                  </Field>
                  <Field label="新密码" icon={<LockKeyhole size={17} />}>
                    <PasswordField
                      name="password"
                      autoComplete="new-password"
                      minLength={8}
                      visible={forgotPasswordVisible}
                      onToggle={() => setForgotPasswordVisible((value) => !value)}
                    />
                  </Field>
                  <Field label="确认新密码" icon={<LockKeyhole size={17} />}>
                    <TextField.Root name="confirm_password" type="password" autoComplete="new-password" minLength={8} required />
                  </Field>
                  <SubmitButton busy={busy} label="重置密码并登录" />
                </form>
              </Tabs.Content>
            </Tabs.Root>

            <Callout.Root className="auth-callout" color={status === "error" ? "red" : status === "success" ? "teal" : "gray"}>
              <Callout.Icon>{checking || status === "submitting" ? <LoaderCircle className="spin" size={17} /> : <ShieldCheck size={17} />}</Callout.Icon>
              <Callout.Text>{message}</Callout.Text>
            </Callout.Root>
          </Flex>
        </Card>
      </section>
    </main>
  );
}

function Field({ label, icon, children }: { label: string; icon: ReactNode; children: ReactNode }) {
  return (
    <label className="auth-field">
      <span>
        {icon}
        {label}
      </span>
      {children}
    </label>
  );
}

function PasswordField({
  name,
  autoComplete,
  minLength,
  visible,
  onToggle
}: {
  name: string;
  autoComplete: string;
  minLength?: number;
  visible: boolean;
  onToggle: () => void;
}) {
  return (
    <TextField.Root name={name} type={visible ? "text" : "password"} autoComplete={autoComplete} minLength={minLength} required>
      <TextField.Slot side="right">
        <button className="password-toggle" type="button" onClick={onToggle} aria-label={visible ? "隐藏密码" : "显示密码"}>
          {visible ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
      </TextField.Slot>
    </TextField.Root>
  );
}

function SubmitButton({ busy, label }: { busy: boolean; label: string }) {
  return (
    <Button className="primary-auth-action" type="submit" size="3" disabled={busy}>
      {busy ? <LoaderCircle className="spin" size={17} /> : null}
      <span>{label}</span>
      {!busy ? <ArrowRight size={17} /> : null}
    </Button>
  );
}

async function postForm(url: string, fields: Record<string, string>) {
  const payload = new FormData();
  Object.entries(fields).forEach(([key, value]) => payload.append(key, value || ""));
  const response = await fetch(url, {
    method: "POST",
    body: payload,
    credentials: "same-origin"
  });
  const data = (await response.json().catch(() => ({}))) as AuthResponse;
  if (!response.ok) {
    throw new Error(data.error || data.detail || "请求失败。");
  }
  return data;
}

function formDataFromForm(form: HTMLFormElement) {
  const data = new FormData(form);
  return Object.fromEntries(Array.from(data.entries()).map(([key, value]) => [key, String(value).trim()]));
}

function safeNextPath(rawNext: string | null) {
  if (!rawNext) return "/";
  try {
    const decoded = decodeURIComponent(rawNext);
    if (!decoded.startsWith("/") || decoded.startsWith("//")) return "/";
    if (decoded.startsWith("/login")) return "/";
    return decoded;
  } catch {
    return "/";
  }
}
