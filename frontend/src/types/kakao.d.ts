declare global {
  interface Window {
    kakao?: {
      maps: {
        load: (callback: () => void) => void;
        Map: new (container: HTMLElement, options: { center: unknown; level: number }) => KakaoMap;
        LatLng: new (lat: number, lng: number) => KakaoLatLng;
        Marker: new (options: { position: KakaoLatLng }) => KakaoMarker;
        Circle: new (options: {
          center: KakaoLatLng;
          radius: number;
          strokeWeight?: number;
          strokeColor?: string;
          strokeOpacity?: number;
          fillColor?: string;
          fillOpacity?: number;
        }) => KakaoCircle;
        services: {
          Status: {
            OK: string;
          };
          Geocoder: new () => {
            addressSearch: (
              query: string,
              callback: (
                result: Array<{ address_name: string; x: string; y: string }>,
                status: string
              ) => void
            ) => void;
          };
        };
      };
    };
  }
}

type KakaoMap = {
  setCenter: (latLng: KakaoLatLng) => void;
  setLevel: (level: number) => void;
};

type KakaoLatLng = object;

type KakaoMarker = {
  setMap: (map: KakaoMap | null) => void;
};

type KakaoCircle = {
  setMap: (map: KakaoMap | null) => void;
};

export {};
