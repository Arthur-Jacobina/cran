import Link from 'next/link';
import { Github, Twitter } from 'lucide-react';
import AnimatedShinyText from '@/components/ui/animated-shiny-text';
export default function Header() {
  return (
    <header className="w-full border-neutral-800 bg-white/50 backdrop-blur-xl sticky top-0 z-50">
      <div className="container mx-auto px-1 py-1 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link href="/">
            <AnimatedShinyText className="text-2xl inline-flex font-bold items-center justify-center px-2 py-1 transition ease-out hover:text-blue-600 hover:duration-300 hover:dark:text-blue-400">
              <span>Cranberry</span>
            </AnimatedShinyText>
          </Link>
        </div>

        <nav className="flex items-center gap-6">
          <Link
            href="https://x.com/Arthur1Jacobina"
            target="_blank"
            className="text-neutral-400 hover:text-blue-400 transition-colors"
          >
            <Twitter size={20} />
          </Link>
          <Link
            href="https://github.com/Arthur-Jacobina/cran"
            target="_blank"
            className="text-neutral-400 hover:text-blue-400 transition-colors"
          >
            <Github size={20} />
          </Link>
        </nav>
      </div>
    </header>
  );
}
