/**
 * Version endpoint - returns build metadata.
 * 
 * Metadata is injected at Docker build time via build args.
 * Returns 'unknown' for any missing values (no crashes).
 */
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    service: 'frontend',
    git_commit: process.env.GIT_COMMIT || 'unknown',
    build_time_utc: process.env.BUILD_TIME_UTC || 'unknown',
    image_tag: process.env.IMAGE_TAG || 'unknown',
  });
}

