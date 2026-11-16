'use strict';

/**
 * The audit as data.
 *
 * 235 directories, each one loaded in a headless browser, with the field count,
 * the login/CAPTCHA flags and the outcome of every submission attempt.
 *
 * The point of shipping it as a package is that the interesting queries are
 * joins, not lookups: "which directories accepted something without requiring
 * an account" is one filter over two files, and nobody wants to re-scrape for it.
 */

const path = require('path');

const dataset = require(path.join(__dirname, 'data', 'ai-directories.json'));

const directories = dataset.directories;
const summary = dataset.summary;

/** Directories that took a submission and confirmed it. Sorted by acceptances. */
function accepted() {
  return directories
    .filter(d => d.accepted > 0)
    .sort((a, b) => b.accepted - a.accepted);
}

/** Directories a script could fill today: a real form, no account, no CAPTCHA. */
function automatable() {
  return directories.filter(d => d.auto_submit);
}

/** Directories that look like forms but render a single newsletter or search input. */
function thinForms(max = 1) {
  return directories.filter(d => d.fillable_fields <= max);
}

/** Group by the source list each directory came from. */
function byCategory() {
  return directories.reduce((acc, d) => {
    const key = d.category || 'unknown';
    acc[key] = acc[key] || { directories: 0, automatable: 0, accepted: 0 };
    acc[key].directories += 1;
    if (d.auto_submit) acc[key].automatable += 1;
    acc[key].accepted += d.accepted;
    return acc;
  }, {});
}

/**
 * Acceptance rate per directory, as a percentage of attempts made against it.
 * Directories with no attempts are excluded rather than counted as zero, which
 * would drag every average toward zero for reasons that have nothing to do
 * with the directory.
 */
function acceptanceRates() {
  return directories
    .filter(d => d.attempts > 0)
    .map(d => ({
      domain: d.domain,
      attempts: d.attempts,
      accepted: d.accepted,
      rate: Math.round((d.accepted / d.attempts) * 1000) / 10
    }))
    .sort((a, b) => b.rate - a.rate || b.accepted - a.accepted);
}

/** Free-text search across domain, category and the recorded rejection reason. */
function search(query) {
  const q = String(query || '').toLowerCase();
  if (!q) return directories;
  return directories.filter(d =>
    [d.domain, d.category, d.reason].some(v => String(v || '').toLowerCase().includes(q))
  );
}

module.exports = {
  dataset,
  directories,
  summary,
  accepted,
  automatable,
  thinForms,
  byCategory,
  acceptanceRates,
  search
};
