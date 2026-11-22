import test from "node:test";
import assert from "node:assert/strict";
import { createTransport } from "../src/features/drive/contents/carrot_navi/transport.js";

class FakeWebSocket {
  static OPEN = 1;
  static instances = [];

  constructor(url) {
    this.url = url;
    this.readyState = 0;
    this.closed = false;
    this.listeners = new Map();
    FakeWebSocket.instances.push(this);
  }

  addEventListener(type, handler) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(handler);
  }

  emit(type, event = {}) {
    for (const handler of this.listeners.get(type) || []) handler(event);
  }

  close() {
    this.closed = true;
  }
}

class FakeWorker {
  postMessage() {}
  addEventListener() {}
  terminate() {}
}

function createHarness(layoutProvider) {
  FakeWebSocket.instances = [];
  globalThis.Worker = FakeWorker;
  const timers = [];
  const target = {
    URL,
    WebSocket: FakeWebSocket,
    location: { href: "http://192.168.0.2:8088/", protocol: "http:" },
    CarrotStreamIdentity: { clientId: "test-client" },
    setTimeout(callback) {
      timers.push(callback);
      return timers.length;
    },
    clearTimeout() {},
  };
  const options = {
    target,
    resolveAssetUrl: () => "/worker.js",
    reconnectMs: 100,
  };
  if (layoutProvider) options.layoutProvider = layoutProvider;
  const transport = createTransport(options);
  transport.start();
  const state = FakeWebSocket.instances[0];
  state.emit("message", {
    data: JSON.stringify({
      type: "carrotNaviSession",
      status: "accepted",
      code: "carrot_navi_accepted",
    }),
  });
  return { transport, timers };
}

function mediaSockets() {
  return FakeWebSocket.instances.filter((socket) => socket.url.includes("/ws/carrot_navi/media"));
}

function layoutOf(socket) {
  return new URL(socket.url).searchParams.get("layout");
}

test("media socket carries the current layout and the state socket does not", () => {
  createHarness(() => "wide");

  const state = FakeWebSocket.instances.find((socket) => socket.url.includes("/ws/carrot_navi/state"));
  assert.equal(new URL(state.url).searchParams.get("layout"), null);
  assert.equal(mediaSockets().length, 1);
  assert.equal(layoutOf(mediaSockets()[0]), "wide");
});

test("no layout provider leaves the media url unchanged", () => {
  createHarness(null);

  assert.equal(mediaSockets().length, 1);
  assert.equal(layoutOf(mediaSockets()[0]), null);
});

test("syncLayout reconnects the media socket only when the layout changed", () => {
  let layout = "tall";
  const { transport, timers } = createHarness(() => layout);
  const first = mediaSockets()[0];
  assert.equal(layoutOf(first), "tall");

  assert.equal(transport.syncLayout(), false);
  assert.equal(first.closed, false);
  assert.equal(timers.length, 0);

  layout = "wide";
  assert.equal(transport.syncLayout(), true);
  assert.equal(first.closed, true);
  assert.equal(timers.length, 1);

  timers.shift()();
  assert.equal(mediaSockets().length, 2);
  assert.equal(layoutOf(mediaSockets()[1]), "wide");
  assert.equal(transport.syncLayout(), false);
});
