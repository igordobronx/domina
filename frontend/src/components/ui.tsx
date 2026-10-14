import type { ReactNode } from "react";
import { Pressable, Text, View } from "react-native";
import type { LucideIcon } from "lucide-react";
import { ArrowUpRight, X } from "lucide-react";
import { colors as c, fonts } from "../theme";

export function Label({
  children,
  muted = false,
  style,
}: {
  children: ReactNode;
  muted?: boolean;
  style?: object;
}) {
  return (
    <Text
      style={[
        {
          fontFamily: fonts.body,
          color: muted ? c.muted : c.ink,
          fontSize: 14,
          lineHeight: 21,
        },
        style,
      ]}
    >
      {children}
    </Text>
  );
}
export function Button({
  children,
  onPress,
  variant = "primary",
  icon: Icon,
  disabled = false,
  small = false,
}: {
  children: ReactNode;
  onPress: () => void;
  variant?: "primary" | "secondary" | "ghost" | "dark";
  icon?: LucideIcon;
  disabled?: boolean;
  small?: boolean;
}) {
  const color = variant === "primary" || variant === "dark" ? c.white : c.ink;
  return (
    <Pressable
      role="button"
      disabled={disabled}
      onPress={onPress}
      style={({
        hovered,
        pressed,
      }: {
        hovered?: boolean;
        pressed: boolean;
      }) => ({
        flexDirection: "row",
        gap: 9,
        alignItems: "center",
        justifyContent: "center",
        minHeight: 44,
        paddingHorizontal: small ? 14 : 20,
        paddingVertical: 11,
        borderRadius: 10,
        backgroundColor:
          variant === "primary"
            ? c.greenText
            : variant === "dark"
              ? c.ink
              : variant === "secondary"
                ? c.white
                : "transparent",
        borderWidth: variant === "secondary" ? 1 : 0,
        borderColor: c.line,
        opacity: disabled ? 0.45 : pressed ? 0.7 : hovered ? 0.88 : 1,
      })}
    >
      {Icon && <Icon size={17} color={color} strokeWidth={1.8} />}
      <Text
        style={{
          fontFamily: fonts.body,
          fontSize: 14,
          fontWeight: "600",
          color,
        }}
      >
        {children}
      </Text>
    </Pressable>
  );
}
export function IconButton({
  icon: Icon,
  label,
  onPress,
}: {
  icon: LucideIcon;
  label: string;
  onPress: () => void;
}) {
  return (
    <Pressable
      role="button"
      aria-label={label}
      onPress={onPress}
      style={({ hovered }: { hovered?: boolean; pressed: boolean }) => ({
        width: 44,
        height: 44,
        borderRadius: 10,
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: hovered ? "#EAE7DE" : "transparent",
      })}
    >
      <Icon size={21} color={c.ink} strokeWidth={1.7} />
    </Pressable>
  );
}
export function Badge({
  children,
  tone = "green",
}: {
  children: ReactNode;
  tone?: "green" | "amber" | "neutral";
}) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={`card ${className}`}>{children}</section>;
}
export function SectionTitle({
  title,
  action,
  onAction,
}: {
  title: string;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <div className="section-title">
      <h2>{title}</h2>
      {action && (
        <button className="text-link" onClick={onAction}>
          {action}
          <ArrowUpRight size={16} />
        </button>
      )}
    </div>
  );
}
export function Progress({
  value,
  label,
  amber = false,
}: {
  value: number;
  label: string;
  amber?: boolean;
}) {
  return (
    <div
      className="progress-track"
      role="progressbar"
      aria-label={label}
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className={amber ? "amber-fill" : ""}
        style={{ width: `${value}%` }}
      />
    </div>
  );
}
export function Logo({
  compact = false,
  light = false,
}: {
  compact?: boolean;
  light?: boolean;
}) {
  return (
    <div className={`logo ${light ? "logo-light" : ""}`} aria-label="Domina">
      <svg width="37" height="43" viewBox="0 0 42 48" aria-hidden="true">
        <path
          d="M9 7h10a17 17 0 0 1 0 34H9"
          stroke="#DCD8CC"
          strokeWidth="7"
          fill="none"
        />
        <path
          d="M9 7h10a17 17 0 0 1 10 31"
          stroke="#2E9E73"
          strokeWidth="7"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M9 7v34"
          stroke={light ? "#F5F3EC" : "#141A2E"}
          strokeWidth="7"
          strokeLinecap="round"
        />
      </svg>
      {!compact && (
        <span>
          domina<span className="logo-ai">.ai</span>
        </span>
      )}
    </div>
  );
}
export function Empty({
  title,
  text,
  children,
}: {
  title: string;
  text: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty">
      <div className="empty-symbol">✓</div>
      <h3>{title}</h3>
      <p>{text}</p>
      {children}
    </div>
  );
}
export function Modal({
  title,
  children,
  onClose,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="section-title">
          <h2>{title}</h2>
          <IconButton icon={X} label="Fechar janela" onPress={onClose} />
        </div>
        {children}
      </section>
    </div>
  );
}
export function Row({ children }: { children: ReactNode }) {
  return (
    <View
      style={{
        flexDirection: "row",
        alignItems: "center",
        gap: 12,
        flexWrap: "wrap",
      }}
    >
      {children}
    </View>
  );
}
