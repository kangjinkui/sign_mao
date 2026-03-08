export type GeocodeCandidate = {
  candidate_id: string;
  address: string;
  lat: number;
  lng: number;
};

export type RadiusItem = {
  id: number;
  company: string;
  ad_type: string;
  address: string;
  lat: number;
  lng: number;
  distance_m: number;
  permit_date?: string | null;
  size_text?: string | null;
};

export type RadiusResponse = {
  input: {
    address: string;
    lat: number;
    lng: number;
  };
  radius: number;
  count: number;
  items: RadiusItem[];
  geocode_candidates: GeocodeCandidate[];
};
