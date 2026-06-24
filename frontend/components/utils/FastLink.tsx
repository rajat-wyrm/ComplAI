import Link from 'next/link';
import type { ReactNode } from 'react';

interface FastLinkProps {
  href: string;
  children: ReactNode;
}

export function FastLink({ href, children }: FastLinkProps) {
  return <Link href={href} prefetch>{children}</Link>;
}
