export interface Directory {
  domain: string;
  category: string;
  entry: string;
  handler: string;
  fillable_fields: number;
  matched_fields: number;
  captcha: boolean;
  login_wall: boolean;
  auto_submit: boolean;
  reason: string;
  attempts: number;
  accepted: number;
  last_accepted: string;
}

export interface Summary {
  directories: number;
  auto: number;
  auto_pct: number;
  thin: number;
  thin_pct: number;
  login: number;
  captcha: number;
  attempts: number;
  accepted: number;
  accept_pct: number;
  accepting_dirs: number;
  accepting_pct: number;
  generated: string;
}

export declare const directories: Directory[];
export declare const summary: Summary;
export declare const dataset: {
  name: string;
  description: string;
  generated: string;
  license: string;
  homepage: string;
  summary: Summary;
  directories: Directory[];
};

export declare function accepted(): Directory[];
export declare function automatable(): Directory[];
export declare function thinForms(max?: number): Directory[];
export declare function byCategory(): Record<string, { directories: number; automatable: number; accepted: number }>;
export declare function acceptanceRates(): Array<{ domain: string; attempts: number; accepted: number; rate: number }>;
export declare function search(query: string): Directory[];
