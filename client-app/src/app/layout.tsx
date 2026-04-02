import type { Metadata } from "next";
import { ThemeProvider } from "@/components/theme-provider";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { Nav } from "@/components/custom/nav";
import { IconSmartHome, IconFlask } from "@tabler/icons-react";
import { TopBar } from "@/components/custom/top-bar";
import { ModeToggle } from "@/components/custom/theme-toggle";

export const metadata: Metadata = {
  title: "Heart Disease Prediction System",
  description: "Simple video streaming platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const navItems = [
    { icon: IconSmartHome, title: "Home", href: "/" },
    { icon: IconFlask, title: "Checkup", href: "/checkup" },
  ];
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="w-screen h-screen overflow-hidden bg-background ">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="w-screen h-full relative overflow-scroll flex sm:flex-row flex-col-reverse [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
            <Nav navLinks={navItems} />
            <main className="w-full h-full overflow-y-scroll bg-background flex-1 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
              <TopBar>
                <ModeToggle />
              </TopBar>
              {children}
            </main>
          </div>

          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
