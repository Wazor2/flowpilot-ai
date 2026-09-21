export class AIUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AI_UNAVAILABLE';
  }
}

export class CapabilityUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CAPABILITY_UNAVAILABLE';
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'VALIDATION_ERROR';
  }
}
