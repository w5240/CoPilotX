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
 * Read skill slug from _meta.json
 */
function getSkillSlug(skillPath: string): string | null {
  try {
    const metaPath = join(skillPath, '_meta.json');
    if (existsSync(metaPath)) {
      const meta = JSON.parse(readFileSync(metaPath, 'utf-8'));
      return meta.slug || null;
    }
  } catch {
    // Ignore errors
  }
  return null;
}

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
 * Get exclusive skills list file path
 */
function getExclusiveSkillsListPath(): string {
  return join(getOpenClawSkillsDir(), '.exclusive-skills-list');
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
 * Check if a skill is exclusive (has .exclusive marker file)
 */
function isExclusiveSkill(skillPath: string): boolean {
  return existsSync(join(skillPath, '.exclusive'));
}

/**
 * Read exclusive skills list
 */
export function getExclusiveSkillsList(): string[] {
  try {
    if (existsSync(getExclusiveSkillsListPath())) {
      const content = readFileSync(getExclusiveSkillsListPath(), 'utf-8');
      return content.split('\n').filter(line => line.trim() !== '');
    }
  } catch {
    // Ignore errors
  }
  return [];
}

/**
 * Copy bundled skills to OpenClaw skills directory
 */
function copyBundledSkills(): { copied: number; skipped: number; exclusive: string[] } {
  const bundledDir = getBundledSkillsDir();
  const skillsDir = getOpenClawSkillsDir();

  if (!existsSync(bundledDir)) {
    console.log('[bundled-skills] No bundled skills directory found');
    return { copied: 0, skipped: 0, exclusive: [] };
  }

  ensureDir(skillsDir);

  let copied = 0;
  let skipped = 0;
  const exclusiveSkills: string[] = [];

  const entries = readdirSync(bundledDir, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const skillName = entry.name;
    const sourcePath = join(bundledDir, skillName);
    const destPath = join(skillsDir, skillName);

    // Check if this is an exclusive skill
    const isExclusive = isExclusiveSkill(sourcePath);
    if (isExclusive) {
      const slug = getSkillSlug(sourcePath);
      if (slug) {
        exclusiveSkills.push(slug);
      } else {
        // Fallback to directory name if no slug found
        exclusiveSkills.push(skillName);
      }
    }

    // Skip if skill already exists (don't overwrite user modifications)
    if (existsSync(destPath)) {
      skipped++;
      continue;
    }

    try {
      cpSync(sourcePath, destPath, { recursive: true });
      copied++;
      // console.log(`[bundled-skills] Copied: ${skillName}${isExclusive ? ' (exclusive)' : ''}`);
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

  // Write exclusive skills list
  try {
    const exclusiveListPath = getExclusiveSkillsListPath();
    const exclusiveListDir = join(exclusiveListPath, '..');
    ensureDir(exclusiveListDir);
    const fs = require('fs');
    fs.writeFileSync(exclusiveListPath, exclusiveSkills.join('\n'));
    // console.log(`[bundled-skills] Exclusive skills: ${exclusiveSkills.length}`);
  } catch (error) {
    console.error('[bundled-skills] Failed to write exclusive skills list:', error);
  }

  return { copied, skipped, exclusive: exclusiveSkills };
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
  const { copied, skipped, exclusive } = copyBundledSkills();

  // console.log(`[bundled-skills] Complete: ${copied} copied, ${skipped} skipped, ${exclusive.length} exclusive`);
}