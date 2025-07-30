declare module "*.svg" {
  import * as React from "react";
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}

interface Window {
  // API configuration
  REACT_APP_API_URL?: string;
  REACT_APP_API_KEY?: string;

  // Streamlit integration
  Streamlit?: any;

  // Custom events
  dispatchEvent(event: Event): boolean;
  addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void;
  removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void;
}

// Custom events for component communication
interface CustomEventMap {
  "switchSearch": CustomEvent<{
    searchId: string;
    search: any;
  }>;
}

declare global {
  interface WindowEventMap extends CustomEventMap {}
}

// Add support for environment variables
declare namespace NodeJS {
  interface ProcessEnv {
    REACT_APP_API_URL: string;
    REACT_APP_API_KEY: string;
    NODE_ENV: 'development' | 'production';
  }
}
