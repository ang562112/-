import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "LLM Multifactor Read-only Dashboard",
  description: "Ticker-based analysis with freshness/confidence checks",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
