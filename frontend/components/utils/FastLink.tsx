import Link from 'next/link';

export function FastLink({ href, children }) {
  return <Link href={href} prefetch>{children}</Link>;
}
