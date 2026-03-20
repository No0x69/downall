import Background from "@/components/Background";
import Hero from "@/components/Hero";
import UrlInput from "@/components/UrlInput";
import DownloadModal from "@/components/DownloadModal";
import DownloadHistory from "@/components/DownloadHistory";

export default function Home() {
  return (
    <>
      <Background />
      <div className="container">
        <Hero />
        <UrlInput />
        <DownloadHistory />
      </div>
      <DownloadModal />
    </>
  );
}
