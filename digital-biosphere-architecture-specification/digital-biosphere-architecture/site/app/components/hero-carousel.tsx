"use client";

import { useEffect, useRef, useState } from "react";
import type { Locale } from "../site-content";

const AUTO_ADVANCE_MS = 8000;

const slides = {
  zh: [
    {
      id: "titmas-infrastructure",
      eyebrow: "TITMAS / 智能体行动控制与可验证执行平台",
      title: "让 AI 智能体犯错时，也不能直接造成未经验证的后果",
      description: "闭源私有核心连接行动闸门、可验证执行回执、证据审计和智能体健康；当前提供公开发现与合成证明，不宣称生产可用。",
      primary: ["申请私有评估", "/private-evaluation/"],
      secondary: ["查看效果证明", "/commercial-evaluation/"],
      status: "私有商业试点候选 · 非生产",
    },
    {
      id: "monitor-pilot",
      eyebrow: "MONITOR BEFORE ENFORCE / 先观察，后控制",
      title: "先看哪些动作本应被阻断，再决定是否进入执行控制",
      description: "Monitor Mode 产生 Shadow Decision、技术回执和审计时间线，不阻断、不执行、不改变客户系统。",
      primary: ["了解 Monitor Pilot", "/monitor-pilot/"],
      secondary: ["查看行动闸门", "/products/gate/"],
      status: "合成参考已实现 · 尚未开放 Offering",
    },
    {
      id: "product-suite",
      eyebrow: "GATE · RECEIPT · AUDIT · HEALTH",
      title: "一个私有平台，四个对外产品",
      description: "Gate 控制关键行动，Receipt 提供可携带证明，Audit 支持复核与重放，Health 识别接入缺口。",
      primary: ["查看四产品目录", "/product-catalog.json"],
      secondary: ["打开 Trust Center", "/trust-center/"],
      status: "公开接口不等于私有实现",
    },
  ],
  en: [
    {
      id: "titmas-infrastructure",
      eyebrow: "TITMAS / AGENT ACTION CONTROL AND VERIFIABLE ACCOUNTABILITY",
      title: "An AI agent mistake should not directly create an unverified consequence",
      description: "A closed private core connects action gates, verifiable execution receipts, evidence audit, and agent health. Public discovery and synthetic proof do not establish production availability.",
      primary: ["Request a private evaluation", "/en/private-evaluation/"],
      secondary: ["View synthetic proof", "/en/commercial-evaluation/"],
      status: "Private commercial-pilot candidate · non-production",
    },
    {
      id: "monitor-pilot",
      eyebrow: "MONITOR BEFORE ENFORCE",
      title: "Observe which actions should be blocked before enabling enforcement",
      description: "Monitor Mode creates Shadow Decisions, technical Receipts, and an Audit timeline without blocking, executing, or changing the customer system.",
      primary: ["Understand Monitor Pilot", "/en/monitor-pilot/"],
      secondary: ["View TITMAS Gate", "/en/products/gate/"],
      status: "Synthetic reference implemented · no available offering",
    },
    {
      id: "product-suite",
      eyebrow: "GATE · RECEIPT · AUDIT · HEALTH",
      title: "One private platform, four public products",
      description: "Gate controls critical actions, Receipt carries proof, Audit supports review and replay, and Health identifies onboarding gaps.",
      primary: ["Open the product catalog", "/product-catalog.json"],
      secondary: ["Open Trust Center", "/en/trust-center/"],
      status: "Public interface is not private implementation",
    },
  ],
} as const;

export function HeroCarousel({ locale }: { locale: Locale }) {
  const items = slides[locale];
  const [activeIndex, setActiveIndex] = useState(0);
  const [userPaused, setUserPaused] = useState(false);
  const [interactionPaused, setInteractionPaused] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(true);
  const regionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const syncPreference = () => setReducedMotion(query.matches);
    syncPreference();
    query.addEventListener("change", syncPreference);
    return () => query.removeEventListener("change", syncPreference);
  }, []);

  useEffect(() => {
    if (reducedMotion || userPaused || interactionPaused) return;
    const timer = window.setInterval(() => {
      setActiveIndex((current) => (current + 1) % items.length);
    }, AUTO_ADVANCE_MS);
    return () => window.clearInterval(timer);
  }, [interactionPaused, items.length, reducedMotion, userPaused]);

  function select(index: number) {
    setActiveIndex((index + items.length) % items.length);
    setUserPaused(true);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLElement>) {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    select(activeIndex + (event.key === "ArrowRight" ? 1 : -1));
  }

  const current = items[activeIndex];
  const currentLabel = locale === "zh"
    ? `第 ${activeIndex + 1} 张，共 ${items.length} 张：${current.status}`
    : `Slide ${activeIndex + 1} of ${items.length}: ${current.status}`;

  return (
    <section
      className="hero hero-carousel"
      data-section-id="hero-carousel"
      aria-roledescription={locale === "zh" ? "轮播" : "carousel"}
      aria-label={locale === "zh" ? "TITMAS 重点入口" : "TITMAS featured entries"}
      onMouseEnter={() => setInteractionPaused(true)}
      onMouseLeave={() => setInteractionPaused(false)}
      onFocusCapture={() => setInteractionPaused(true)}
      onBlurCapture={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setInteractionPaused(false);
      }}
      onKeyDown={handleKeyDown}
      ref={regionRef}
    >
      <div className="hero-grid" aria-hidden="true">
        <div className="orbit orbit-a" />
        <div className="orbit orbit-b" />
        <div className="node node-a" />
        <div className="node node-b" />
        <div className="node node-c" />
      </div>

      <div className="hero-carousel-stage">
        {items.map((slide, index) => (
          <article
            className="hero-content hero-slide"
            hidden={index !== activeIndex}
            key={slide.id}
            aria-roledescription={locale === "zh" ? "幻灯片" : "slide"}
            aria-label={locale === "zh" ? `${index + 1}/${items.length}` : `${index + 1} of ${items.length}`}
          >
            {slide.id === "titmas-infrastructure" && (
              <span
                className="hero-brand-logo"
                role="img"
                aria-label={locale === "zh" ? "夏日之海 Logo" : "titmas logo"}
              />
            )}
            <div className="hero-badge"><span />{slide.status}</div>
            <p className="eyebrow">{slide.eyebrow}</p>
            <h1>{slide.title}</h1>
            <p className="hero-lead">{slide.description}</p>
            <div className="hero-actions">
              <a className="button button-primary" href={slide.primary[1]}>{slide.primary[0]}</a>
              <a className="button button-secondary" href={slide.secondary[1]}>{slide.secondary[0]}</a>
            </div>
            {slide.id === "media-evidence" && (
              <p className="truth-notice">
                <span>i</span>
                {locale === "zh"
                  ? "本地合成参考实现；不提供内容真实性认证、身份认证、法律证据或生产审核服务。"
                  : "Local synthetic reference implementation; no content-truth, identity, legal-evidence, or production-review service."}
              </p>
            )}
          </article>
        ))}
      </div>

      <div className="hero-carousel-controls">
        <button type="button" onClick={() => select(activeIndex - 1)} aria-label={locale === "zh" ? "上一张" : "Previous slide"}>←</button>
        <div className="hero-carousel-dots" role="group" aria-label={locale === "zh" ? "选择轮播页" : "Choose a slide"}>
          {items.map((slide, index) => (
            <button
              type="button"
              key={slide.id}
              onClick={() => select(index)}
              aria-label={locale === "zh" ? `显示第 ${index + 1} 张：${slide.status}` : `Show slide ${index + 1}: ${slide.status}`}
              aria-current={index === activeIndex ? "true" : undefined}
            >
              <span aria-hidden="true">{String(index + 1).padStart(2, "0")}</span>
            </button>
          ))}
        </div>
        <button type="button" onClick={() => select(activeIndex + 1)} aria-label={locale === "zh" ? "下一张" : "Next slide"}>→</button>
        <span className="sr-only" aria-live={userPaused ? "polite" : "off"}>{currentLabel}</span>
      </div>
    </section>
  );
}

export const heroCarouselContract = {
  slideCount: 3,
  autoAdvanceMs: AUTO_ADVANCE_MS,
  pausesAfterUserAction: true,
  pausesOnHoverOrFocus: true,
  disablesAutoAdvanceForReducedMotion: true,
  serverRenderedFirstSlide: true,
} as const;
