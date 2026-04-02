"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import maplibregl, { GeoJSONSource, LngLatBoundsLike, Map } from "maplibre-gl";

type Stop = {
  id: string;
  label: string;
  coordinates: [number, number];
  zoom: number;
  bearing: number;
  episode: string;
};

const TOTAL_DURATION_MS = 120_000;
const FLY_DURATION_MS = 8_000;
const DWELL_DURATION_MS = 2_000;
const FINAL_DWELL_MS = 8_000;
const FINAL_ORBIT_MS = 24_000;
const PITCH = 60;
const ROUTE_SOURCE_ID = "journey-route";
const STOPS_SOURCE_ID = "journey-stops";
const CURRENT_STOP_SOURCE_ID = "journey-current-stop";
const MAPTILER_KEY = process.env.NEXT_PUBLIC_MAPTILER_API_KEY;
const STYLE_URL = MAPTILER_KEY
  ? `https://api.maptiler.com/maps/streets-v2/style.json?key=${MAPTILER_KEY}`
  : "https://tiles.openfreemap.org/styles/liberty";

const STOPS: Stop[] = [
  {
    id: "omura",
    label: "大村",
    coordinates: [129.9591, 32.9214],
    zoom: 14.7,
    bearing: 22,
    episode: "生まれてから小学校2年まで過ごしました",
  },
  {
    id: "iwakuni",
    label: "岩国",
    coordinates: [132.1784, 34.1676],
    zoom: 14.9,
    bearing: 36,
    episode: "米軍基地があったので初めて外国人の人を見たのを覚えています",
  },
  {
    id: "kashiwa",
    label: "柏市",
    coordinates: [140.0179, 35.8179],
    zoom: 13.9,
    bearing: 8,
    episode: "関東での新生活。小学校5年生から中学1年まで過ごしました",
  },
  {
    id: "zushi",
    label: "逗子海岸",
    coordinates: [139.5714, 35.2925],
    zoom: 15.3,
    bearing: 144,
    episode:
      "友達とよく海辺まで散歩して陽が落ちるまで浜辺で話すという贅沢をしていました。",
  },
  {
    id: "okurayama",
    label: "大倉山駅",
    coordinates: [139.6277, 35.5317],
    zoom: 16.1,
    bearing: 122,
    episode: "横浜のサッカースタジアムが徒歩圏で、Jリーグ観戦に行ったりしていました",
  },
  {
    id: "toritsudaigaku",
    label: "都立大学駅",
    coordinates: [139.6766, 35.6175],
    zoom: 16.2,
    bearing: 202,
    episode: "一人暮らしを始めた街で、この頃から社会人で、テレビのCG制作をしていました",
  },
  {
    id: "kyodo",
    label: "経堂",
    coordinates: [139.636, 35.6515],
    zoom: 15.8,
    bearing: 287,
    episode: "結婚して初めて住んだ街で、新宿からの終電も止まるし、過ごしやすかったです",
  },
  {
    id: "nishikoyama",
    label: "西小山",
    coordinates: [139.6988, 35.6157],
    zoom: 16,
    bearing: 246,
    episode: "よくテレビロケにも出てくる巨大アーケードが近くにあります。",
  },
  {
    id: "ogikubo",
    label: "荻窪",
    coordinates: [139.6202, 35.7049],
    zoom: 15.7,
    bearing: 18,
    episode: "この頃もまだCG制作をしていて、フリーランスで働いていました",
  },
  {
    id: "okusawa",
    label: "奥沢",
    coordinates: [139.6713, 35.6029],
    zoom: 18.2,
    bearing: 48,
    episode:
      "現在の自宅。グラフィックデザイナー、スタートアップでのUIデザインなどを経て今に至ります。",
  },
];

const ROUTE_LABEL = STOPS.map((stop) => stop.label).join(" → ");

const INITIAL_VIEW = {
  center: [137.15, 35.3] as [number, number],
  zoom: 4.55,
  pitch: 22,
  bearing: -8,
};

function createRouteGeoJson(activeIndex: number) {
  return {
    type: "FeatureCollection" as const,
    features: [
      {
        type: "Feature" as const,
        properties: {},
        geometry: {
          type: "LineString" as const,
          coordinates: STOPS.slice(0, activeIndex + 1).map((stop) => stop.coordinates),
        },
      },
    ],
  };
}

function createStopsGeoJson() {
  return {
    type: "FeatureCollection" as const,
    features: STOPS.map((stop, index) => ({
      type: "Feature" as const,
      properties: {
        id: stop.id,
        label: stop.label,
        order: index + 1,
      },
      geometry: {
        type: "Point" as const,
        coordinates: stop.coordinates,
      },
    })),
  };
}

function createCurrentStopGeoJson(stop: Stop) {
  return {
    type: "FeatureCollection" as const,
    features: [
      {
        type: "Feature" as const,
        properties: {
          id: stop.id,
          label: stop.label,
        },
        geometry: {
          type: "Point" as const,
          coordinates: stop.coordinates,
        },
      },
    ],
  };
}

function wait(ms: number) {
  return new Promise<void>((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function flyToAsync(map: Map, stop: Stop, duration: number) {
  return new Promise<void>((resolve) => {
    const complete = () => {
      map.off("moveend", complete);
      resolve();
    };

    map.on("moveend", complete);
    map.flyTo({
      center: stop.coordinates,
      zoom: stop.zoom,
      pitch: PITCH,
      bearing: stop.bearing,
      duration,
      essential: true,
      speed: 0.45,
      curve: 1.32,
    });
  });
}

async function orbitAroundStop(map: Map, stop: Stop, duration: number) {
  const start = performance.now();
  const initialBearing = map.getBearing();

  return new Promise<void>((resolve) => {
    const frame = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);

      map.jumpTo({
        center: stop.coordinates,
        zoom: stop.zoom,
        pitch: PITCH,
        bearing: initialBearing + 360 * progress,
      });

      if (progress < 1) {
        window.requestAnimationFrame(frame);
      } else {
        resolve();
      }
    };

    window.requestAnimationFrame(frame);
  });
}

function addThreeDimensionalLayers(map: Map) {
  const availableSources = map.getStyle().sources ?? {};
  const buildingSource = availableSources.maptiler_planet
    ? "maptiler_planet"
    : availableSources.openmaptiles
      ? "openmaptiles"
      : null;

  if (!map.getSource(STOPS_SOURCE_ID)) {
    map.addSource(STOPS_SOURCE_ID, {
      type: "geojson",
      data: createStopsGeoJson(),
    });
  }

  if (!map.getSource(CURRENT_STOP_SOURCE_ID)) {
    map.addSource(CURRENT_STOP_SOURCE_ID, {
      type: "geojson",
      data: createCurrentStopGeoJson(STOPS[0]),
    });
  }

  if (!map.getSource(ROUTE_SOURCE_ID)) {
    map.addSource(ROUTE_SOURCE_ID, {
      type: "geojson",
      data: createRouteGeoJson(0),
    });
  }

  if (!map.getLayer("journey-route-glow")) {
    map.addLayer({
      id: "journey-route-glow",
      type: "line",
      source: ROUTE_SOURCE_ID,
      paint: {
        "line-color": "#ffe9b3",
        "line-opacity": 0.35,
        "line-width": 10,
        "line-blur": 8,
      },
    });
  }

  if (!map.getLayer("journey-route-line")) {
    map.addLayer({
      id: "journey-route-line",
      type: "line",
      source: ROUTE_SOURCE_ID,
      paint: {
        "line-color": "#f5a65b",
        "line-width": 4,
        "line-opacity": 0.95,
      },
    });
  }

  if (!map.getLayer("journey-stops")) {
    map.addLayer({
      id: "journey-stops",
      type: "circle",
      source: STOPS_SOURCE_ID,
      paint: {
        "circle-radius": 5,
        "circle-color": "#f9e4c3",
        "circle-stroke-color": "#10202f",
        "circle-stroke-width": 2,
      },
    });
  }

  if (!map.getLayer("journey-current-stop-pulse")) {
    map.addLayer({
      id: "journey-current-stop-pulse",
      type: "circle",
      source: CURRENT_STOP_SOURCE_ID,
      paint: {
        "circle-radius": 18,
        "circle-color": "#f5a65b",
        "circle-opacity": 0.18,
      },
    });
  }

  if (!map.getLayer("journey-current-stop")) {
    map.addLayer({
      id: "journey-current-stop",
      type: "circle",
      source: CURRENT_STOP_SOURCE_ID,
      paint: {
        "circle-radius": 7,
        "circle-color": "#fff8e8",
        "circle-stroke-color": "#f5a65b",
        "circle-stroke-width": 3,
      },
    });
  }

  if (!map.getLayer("journey-stop-labels")) {
    map.addLayer({
      id: "journey-stop-labels",
      type: "symbol",
      source: STOPS_SOURCE_ID,
      layout: {
        "text-field": ["get", "label"],
        "text-font": ["Noto Sans Regular"],
        "text-size": 12,
        "text-offset": [0, 1.2],
      },
      paint: {
        "text-color": "#0e2231",
        "text-halo-color": "#fff8e8",
        "text-halo-width": 1.2,
      },
    });
  }

  if (buildingSource && !map.getLayer("journey-3d-buildings")) {
    map.addLayer({
      id: "journey-3d-buildings",
      type: "fill-extrusion",
      source: buildingSource,
      "source-layer": "building",
      minzoom: 14,
      paint: {
        "fill-extrusion-color": [
          "interpolate",
          ["linear"],
          ["coalesce", ["get", "render_height"], ["get", "height"], 0],
          0,
          "#cbd8df",
          60,
          "#9bb6c4",
          180,
          "#5b7c91",
        ],
        "fill-extrusion-height": [
          "coalesce",
          ["get", "render_height"],
          ["get", "height"],
          10,
        ],
        "fill-extrusion-base": [
          "coalesce",
          ["get", "render_min_height"],
          ["get", "min_height"],
          0,
        ],
        "fill-extrusion-opacity": 0.82,
      },
    });
  }
}

export function JourneyMapExperience() {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [remainingMs, setRemainingMs] = useState(TOTAL_DURATION_MS);

  const activeStop = STOPS[activeIndex];
  const progressPercent = useMemo(() => {
    return ((TOTAL_DURATION_MS - remainingMs) / TOTAL_DURATION_MS) * 100;
  }, [remainingMs]);

  const syncMapData = (index: number) => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const routeSource = map.getSource(ROUTE_SOURCE_ID) as GeoJSONSource | undefined;
    routeSource?.setData(createRouteGeoJson(index));

    const currentSource = map.getSource(CURRENT_STOP_SOURCE_ID) as GeoJSONSource | undefined;
    currentSource?.setData(createCurrentStopGeoJson(STOPS[index]));
  };

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) {
      return;
    }

    const bounds: LngLatBoundsLike = [
      [127.8, 31.6],
      [140.4, 36.6],
    ];

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: STYLE_URL,
      center: INITIAL_VIEW.center,
      zoom: INITIAL_VIEW.zoom,
      pitch: INITIAL_VIEW.pitch,
      bearing: INITIAL_VIEW.bearing,
      maxPitch: 80,
      maxBounds: bounds,
      attributionControl: false,
    });

    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl(), "bottom-right");

    map.on("load", () => {
      addThreeDimensionalLayers(map);
      syncMapData(0);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!isPlaying) {
      return;
    }

    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      const elapsed = Date.now() - startedAt;
      setRemainingMs(Math.max(TOTAL_DURATION_MS - elapsed, 0));
    }, 250);

    return () => {
      window.clearInterval(timer);
    };
  }, [isPlaying]);

  const runJourney = async () => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    setIsPlaying(true);
    setIsFinished(false);
    setRemainingMs(TOTAL_DURATION_MS);
    setActiveIndex(0);
    syncMapData(0);

    map.stop();
    map.easeTo({
      center: INITIAL_VIEW.center,
      zoom: INITIAL_VIEW.zoom,
      pitch: INITIAL_VIEW.pitch,
      bearing: INITIAL_VIEW.bearing,
      duration: 0,
    });

    for (let index = 0; index < STOPS.length; index += 1) {
      const stop = STOPS[index];
      setActiveIndex(index);
      syncMapData(index);
      await flyToAsync(map, stop, FLY_DURATION_MS);

      if (index < STOPS.length - 1) {
        await wait(DWELL_DURATION_MS);
      }
    }

    await wait(FINAL_DWELL_MS);
    await orbitAroundStop(map, STOPS[STOPS.length - 1], FINAL_ORBIT_MS);

    setRemainingMs(0);
    setIsPlaying(false);
    setIsFinished(true);
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground">
      <div ref={mapContainerRef} className="journey-map" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(245,166,91,0.2),_transparent_32%),linear-gradient(180deg,rgba(4,11,17,0.2),rgba(4,11,17,0.68))]" />

      <section className="pointer-events-none absolute inset-0 flex flex-col justify-between p-4 sm:p-6 lg:p-8">
        <div className="journey-panel pointer-events-auto max-w-md rounded-[28px] border border-white/15 bg-surface px-5 py-5 text-sm text-muted shadow-[0_20px_60px_rgba(0,0,0,0.28)] sm:px-6">
          <p className="text-xs uppercase tracking-[0.3em] text-accent-strong">
            移動ログ
          </p>
          <h1 className="mt-3 text-3xl leading-tight text-foreground sm:text-4xl">
            引越し遍歴をめぐる 3D マップ
          </h1>
          <p className="mt-4 text-[11px] uppercase tracking-[0.28em] text-white/55">
            {ROUTE_LABEL}
          </p>
          <div className="mt-5 rounded-2xl border border-white/10 bg-surface-strong px-4 py-4">
            <p className="text-xs uppercase tracking-[0.24em] text-accent-strong">
              現在地
            </p>
            <p className="mt-2 text-2xl font-semibold text-white">{activeStop.label}</p>
            <p className="mt-3 leading-7 text-muted">{activeStop.episode}</p>
          </div>
        </div>

        <div
          className={`flex px-4 text-center transition-all duration-700 ${
            isPlaying || isFinished
              ? "pointer-events-auto absolute top-4 right-4 z-10 w-[min(28rem,calc(100vw-2rem))] flex-col items-stretch gap-3 sm:top-6 sm:right-6 lg:top-8 lg:right-8"
              : "flex-col items-center gap-5 self-center"
          }`}
        >
          <div
            className={`journey-panel pointer-events-auto border border-white/15 bg-surface shadow-[0_18px_40px_rgba(0,0,0,0.25)] transition-all duration-700 ${
              isPlaying || isFinished
                ? "rounded-[24px] px-4 py-3 text-left"
                : "rounded-full px-5 py-3"
            }`}
          >
            <p className="text-xs uppercase tracking-[0.35em] text-white/60">
              自己紹介サイト
            </p>
            <p
              className={`mt-2 font-serif text-white transition-all duration-700 ${
                isPlaying || isFinished ? "text-xl sm:text-2xl" : "text-2xl sm:text-3xl"
              }`}
            >
              120 秒でたどる、人生の旅
            </p>
          </div>

          <button
            type="button"
            onClick={() => {
              if (!isPlaying) {
                void runJourney();
              }
            }}
            disabled={isPlaying}
            className={`pointer-events-auto rounded-full border border-white/20 bg-[linear-gradient(135deg,#f5a65b,#ffd08b)] font-semibold text-[#102030] shadow-[0_18px_55px_rgba(245,166,91,0.4)] transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_24px_65px_rgba(245,166,91,0.46)] disabled:cursor-not-allowed disabled:opacity-70 ${
              isPlaying || isFinished
                ? "w-full px-6 py-3 text-base"
                : "min-w-64 px-8 py-4 text-lg"
            }`}
          >
            {isPlaying ? "移動中..." : "人生の旅をスタート"}
          </button>

          <div
            className={`journey-panel pointer-events-auto rounded-[24px] border border-white/15 bg-surface px-4 py-4 text-left shadow-[0_18px_40px_rgba(0,0,0,0.25)] transition-all duration-700 ${
              isPlaying || isFinished ? "w-full" : "w-[min(88vw,28rem)]"
            }`}
          >
            <div className="flex items-center justify-between text-sm text-white/80">
              <span>旅の進行状況</span>
              <span>{(remainingMs / 1000).toFixed(1)} 秒</span>
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-[linear-gradient(90deg,#f5a65b,#fff1c7)] transition-[width] duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="mt-3 text-sm leading-6 text-muted">
              {isFinished
                ? "奥沢に到着。いまの暮らしを包む景色を見渡して、旅はここでひと息つきます。"
                : `大村から奥沢まで、${STOPS.length}つの拠点を順番に飛びながら現在地とエピソードを更新します。`}
            </p>
            <p className="mt-2 text-xs uppercase tracking-[0.24em] text-white/45">
              {MAPTILER_KEY ? "MapTiler style enabled" : "Fallback style enabled"}
            </p>
          </div>
        </div>

        <div className="self-end">
          <div className="journey-panel rounded-[24px] border border-white/15 bg-surface px-4 py-3 text-right text-sm text-white/70 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <p className="text-xs uppercase tracking-[0.3em] text-accent-strong">
              Ending
            </p>
            <p className="mt-2 font-serif text-xl text-white">最後は奥沢を 360° Orbit</p>
          </div>
        </div>
      </section>
    </main>
  );
}
