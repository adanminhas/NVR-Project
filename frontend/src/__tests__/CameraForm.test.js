import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import CameraForm from "../components/CameraForm.vue";

describe("CameraForm", () => {
  it("calls onSave with the trimmed form values", async () => {
    const onSave = vi.fn().mockResolvedValue();
    const wrapper = mount(CameraForm, {
      props: { initial: { name: "", rtsp_url: "" }, onSave },
    });

    await wrapper.find('input[type="text"]').setValue("Front door");
    await wrapper.findAll('input[type="text"]')[1].setValue("rtsp://cam.example/1");

    await wrapper.find("form").trigger("submit.prevent");

    expect(onSave).toHaveBeenCalledTimes(1);
    expect(onSave).toHaveBeenCalledWith({
      name: "Front door",
      rtsp_url: "rtsp://cam.example/1",
    });
  });

  it("shows the server error message when onSave throws", async () => {
    const onSave = vi.fn().mockRejectedValue({
      response: { data: { detail: "Boom from server" } },
    });
    const wrapper = mount(CameraForm, {
      props: { initial: { name: "x", rtsp_url: "rtsp://x" }, onSave },
    });

    await wrapper.find("form").trigger("submit.prevent");
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Boom from server");
  });

  it("emits cancel when Cancel is clicked", async () => {
    const wrapper = mount(CameraForm, {
      props: { initial: { name: "", rtsp_url: "" }, onSave: vi.fn() },
    });
    await wrapper.find("button[type='button']").trigger("click");
    expect(wrapper.emitted().cancel).toBeTruthy();
  });
});
