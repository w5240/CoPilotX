/**
 * Initialize bundled skills
 * 
 * Copies pre-bundled skills from app resources to ~/.openclaw/skills
 * on first launch or when bundled skills are updated.
 */

import { app } from 'electron';
import { existsSync, readFileSync, readdirSync, cpSync, mkdirSync } from 'fs';
import { join } from 'path';
import { getOpenClawSkillsDir, getResourcesDir, ensureDir } from './paths';

/**
 * Get bundled skills directory
 */
function getBundledSkillsDir(): string {
  if (app.isPackaged) {
    return join(process.resourcesPath, 'bundled-skills');
  }
  // Development: use resources/bundled-skills
  return join(__dirname, '../../resources/bundled-skills');
}

/**
 * Get version marker file path
 */
function getVersionMarkerPath(): string {
  return join(getOpenClawSkillsDir(), '.bundled-skills-version');
}

/**
 * Read current bundled skills version
 */
function getBundledVersion(): string {
  try {
    const versionFile = join(getBundledSkillsDir(), '.version');
    if (existsSync(versionFile)) {
      return readFileSync(versionFile, 'utf-8').trim();
    }
  } catch {
    // Ignore errors
  }
  return 'unknown';
}

/**
 * Read installed version marker
 */
function getInstalledVersion(): string | null {
  try {
    if (existsSync(getVersionMarkerPath())) {
      return readFileSync(getVersionMarkerPath(), 'utf-8').trim();
    }
  } catch {
    // Ignore errors
  }
  return null;
}

/**
 * Copy bundled skills to OpenClaw skills directory
 */
function copyBundledSkills(): { copied: number; skipped: number } {
  const bundledDir = getBundledSkillsDir();
  const skillsDir = getOpenClawSkillsDir();

  if (!existsSync(bundledDir)) {
    console.log('[bundled-skills] No bundled skills directory found');
    return { copied: 0, skipped: 0 };
  }

  ensureDir(skillsDir);

  let copied = 0;
  let skipped = 0;

  const entries = readdirSync(bundledDir, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const skillName = entry.name;
    const sourcePath = join(bundledDir, skillName);
    const destPath = join(skillsDir, skillName);

    // Skip if skill already exists (don't overwrite user modifications)
    if (existsSync(destPath)) {
      skipped++;
      continue;
    }

    try {
      cpSync(sourcePath, destPath, { recursive: true });
      copied++;
      console.log(`[bundled-skills] Copied: ${skillName}`);
    } catch (error) {
      console.error(`[bundled-skills] Failed to copy ${skillName}:`, error);
    }
  }

  // Write version marker
  const version = getBundledVersion();
  try {
    const versionPath = getVersionMarkerPath();
    const versionDir = join(versionPath, '..');
    ensureDir(versionDir);
    const fs = require('fs');
    fs.writeFileSync(versionPath, version);
  } catch (error) {
    console.error('[bundled-skills] Failed to write version marker:', error);
  }

  return { copied, skipped };
}

/**
 * Initialize bundled skills
 * Should be called on app startup
 */
export function initializeBundledSkills(): void {
  const bundledVersion = getBundledVersion();
  const installedVersion = getInstalledVersion();

  console.log(`[bundled-skills] Bundled version: ${bundledVersion}`);
  console.log(`[bundled-skills] Installed version: ${installedVersion || 'none'}`);

  // Skip if already installed and version matches
  if (installedVersion === bundledVersion) {
    console.log('[bundled-skills] Already up to date, skipping');
    return;
  }

  console.log('[bundled-skills] Initializing bundled skills...');
  const { copied, skipped } = copyBundledSkills();

  console.log(`[bundled-skills] Complete: ${copied} copied, ${skipped} skipped`);
}