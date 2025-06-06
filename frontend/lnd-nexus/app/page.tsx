import Hero from "./components/Hero";
import HowItWorks from "./components/HowItWorks";
import FeaturedProfessionals from "./components/FeaturedProfessionals";
import FeaturedJobs from "./components/FeaturedJobs";
import FeaturedProjects from "./components/FeaturedProjects";
import ResourceHub from "./components/ResourceHub";
import Testimonials from "./components/Testimonials";
import Pricing from "./components/Pricing";
import CTA from "./components/CTA";

export default function Home() {
  return (
    <main>
      <Hero />
      <HowItWorks />
      <FeaturedProfessionals />
      <FeaturedJobs />
      <FeaturedProjects />
      <ResourceHub />
      <Testimonials />
      <Pricing />
      <CTA />
    </main>
  )
}
