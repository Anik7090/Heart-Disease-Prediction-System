"use client";
import Link from "next/link";
import React from "react";
import { Button } from "@/components/ui/button";
import { IconReportMedical, IconHeartbeat } from "@tabler/icons-react";
import Image from "next/image";
export default function Home() {
  return (
    <div
      className="w-full min-h-[calc(100vh-72px)] flex items-center py-12 p-6"
      style={{ background: "transparent" }}
    >
      <main className="grid grid-cols-1 lg:grid-cols-2 place-items-center">
        <div className="space-y-6">
          <h1
            className="text-4xl sm:text-5xl font-extrabold leading-tight"
            style={{ color: "var(--color-foreground)" }}
          >
            Predict your heart health in seconds.
          </h1>

          <p
            className="text-sm max-w-xl"
            style={{ color: "var(--muted-foreground)" }}
          >
            Predict your heart health in seconds with fast, intelligent systems
            that analyse key medical indicators instantly. Using advanced
            Machine Learning technologies, they provide quick and reliable
            insights into your heart’s condition, helping you make informed
            decisions for better health.
          </p>

          <div className="flex flex-wrap gap-3 items-center">
            <Link href="/checkup" className="inline-block ">
              <Button size="lg" variant={"destructive"}>
                <span className="mr-2 -mt-0.5">
                  <IconHeartbeat size={18} />
                </span>
                Check now
              </Button>
            </Link>

            <Link href="/model-info/ui" className="inline-block">
              <Button variant="ghost" size="lg" color="">
                <span className="mr-2 -mt-0.5">
                  <IconReportMedical size={16} />
                </span>
                Model Info
              </Button>
            </Link>
          </div>
          <div
            className="mt-2 text-sm"
            style={{ color: "var(--muted-foreground)" }}
          >
            Quick tip: Always consult a doctor for confirmation—machine
            predictions help, but professional medical advice is essential for
            accurate heart diagnosis..
          </div>
        </div>
        <div
          className="p-0 shadow-xl rounded-2xl overflow-hidden"
          style={{
            background:
              "linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))",
            height: "100%",
          }}
        >
          <Image
            src={"/content2.webp"}
            width={500}
            height={200}
            alt="hero-banner"
            className="w-full"
          />
          <div className="w-full h-max flex items-center justify-center border p-8 bg-accent">
            <Image
              src={"/hero-beat.png"}
              width={400}
              height={50}
              alt="hero-beat"
            />
          </div>
        </div>
      </main>
    </div>
  );
}
