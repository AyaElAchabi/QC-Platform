import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('mlops_access_token')?.value
  const { pathname } = request.nextUrl

  // Routes publiques
  const publicPaths = ['/auth/login', '/auth/register', '/about']
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path))

  // Page d'accueil (/) est accessible à tous
  if (pathname === '/') {
    return NextResponse.next()
  }

  // Si l'utilisateur n'est pas connecté et tente d'accéder à une route protégée
  if (!isPublicPath && !token) {
    console.log('🔒 Middleware: Pas de token, redirection vers /auth/login depuis', pathname)
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  // Si l'utilisateur est connecté et tente d'accéder à login/register
  if (isPublicPath && token && pathname !== '/') {
    console.log('🔓 Middleware: Token trouvé, redirection vers /dashboard depuis', pathname)
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\.svg|.*\\.png).*)'],
}
