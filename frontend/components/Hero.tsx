"use client";

export default function Hero() {
  const platforms = [
    { name: "YouTube", emoji: "▶️", color: "#FF0000" },
    { name: "Instagram", emoji: "📷", color: "#E1306C" },
    { name: "Facebook", emoji: "📘", color: "#1877F2" },
    { name: "TikTok", emoji: "🎵", color: "#69C9D0" },
  ];

  return (
    <section className="hero">
      <div className="hero__eyebrow">
        <span className="hero__badge">✨ Free • Fast • Premium</span>
      </div>
      <h1 className="hero__title">
        Download Any{" "}
        <span className="hero__gradient-text">Video or Audio</span>
        <br />
        in Seconds
      </h1>
      <p className="hero__subtitle">
        Supports YouTube, Instagram, Facebook & TikTok. Choose your format,
        pick your quality, and download instantly — no sign-up required.
      </p>
      <div className="hero__platforms">
        {platforms.map((p) => (
          <div
            key={p.name}
            className="hero__platform-chip"
            style={{ "--chip-color": p.color } as React.CSSProperties}
          >
            <span>{p.emoji}</span>
            <span>{p.name}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
