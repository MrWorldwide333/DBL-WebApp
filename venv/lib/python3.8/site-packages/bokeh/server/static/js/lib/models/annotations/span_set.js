import { Annotation, AnnotationView } from "./annotation";
import { ColumnDataSource } from "../sources/column_data_source";
import { display, undisplay, div } from "../../core/dom";
import * as p from "../../core/properties";
import { bk_annotation_child } from "../../styles/annotations";
export class SpanSetView extends AnnotationView {
    initialize() {
        super.initialize();
        this.set_data(this.model.source);
        this.plot_view.canvas_view.add_overlay(this.el);
        this.el.style.position = "absolute";
        undisplay(this.el);
        if (this.model.render_mode == 'css') {
            for (let i = 0, end = this._location.length; i < end; i++) {
                const el = div({ class: bk_annotation_child });
                this.el.appendChild(el);
            }
        }
    }
    connect_signals() {
        super.connect_signals();
        if (this.model.render_mode == 'css') {
            // dispatch CSS update immediately
            this.connect(this.model.change, () => {
                this.set_data(this.model.source);
                this.render();
            });
            this.connect(this.model.source.streaming, () => {
                this.set_data(this.model.source);
                this.render();
            });
            this.connect(this.model.source.patching, () => {
                this.set_data(this.model.source);
                this.render();
            });
            this.connect(this.model.source.change, () => {
                this.set_data(this.model.source);
                this.render();
            });
        }
        else {
            this.connect(this.model.change, () => {
                this.set_data(this.model.source);
                this.plot_view.request_render();
            });
            this.connect(this.model.source.streaming, () => {
                this.set_data(this.model.source);
                this.plot_view.request_render();
            });
            this.connect(this.model.source.patching, () => {
                this.set_data(this.model.source);
                this.plot_view.request_render();
            });
            this.connect(this.model.source.change, () => {
                this.set_data(this.model.source);
                this.plot_view.request_render();
            });
        }
    }
    set_data(source) {
        super.set_data(source);
        this.visuals.warm_cache(source);
    }
    render() {
        if (this.model.render_mode == 'css') {
            if (this.model.visible)
                display(this.el);
            else
                undisplay(this.el);
        }
        if (!this.model.visible)
            return;
        for (let i = 0, end = this._location.length; i < end; i++) {
            this._draw_span_set(i, this._location[i]);
        }
    }
    _draw_span_set(i, loc) {
        const { frame } = this.plot_view;
        const xscale = frame.xscales[this.model.x_range_name];
        const yscale = frame.yscales[this.model.y_range_name];
        const _calc_dim = (scale, view) => {
            if (this.model.location_units == 'data')
                return scale.compute(loc);
            else
                return view.compute(loc);
        };
        let height, sleft, stop, width;
        if (this.model.dimension == 'width') {
            stop = _calc_dim(yscale, frame.yview);
            sleft = frame._left.value;
            width = frame._width.value;
            height = this.model.properties.line_width.value();
        }
        else {
            stop = frame._top.value;
            sleft = _calc_dim(xscale, frame.xview);
            width = this.model.properties.line_width.value();
            height = frame._height.value;
        }
        if (this.model.render_mode == "css") {
            const el = this.el.children[i];
            el.style.position = 'absolute';
            el.style.top = `${stop}px`;
            el.style.left = `${sleft}px`;
            el.style.width = `${width}px`;
            el.style.height = `${height}px`;
            el.style.backgroundColor = this.model.properties.line_color.value();
            el.style.opacity = this.model.properties.line_alpha.value();
        }
        else if (this.model.render_mode == "canvas") {
            const { ctx } = this.plot_view.canvas_view;
            ctx.save();
            ctx.beginPath();
            this.visuals.line.set_value(ctx);
            ctx.moveTo(sleft, stop);
            if (this.model.dimension == "width") {
                ctx.lineTo(sleft + width, stop);
            }
            else {
                ctx.lineTo(sleft, stop + height);
            }
            ctx.stroke();
            ctx.restore();
        }
    }
}
SpanSetView.__name__ = "SpanSetView";
export class SpanSet extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
    static init_SpanSet() {
        this.prototype.default_view = SpanSetView;
        this.mixins(['line']);
        this.define({
            render_mode: [p.RenderMode, 'canvas'],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
            location: [p.NumberSpec],
            location_units: [p.SpatialUnits, 'data'],
            dimension: [p.Dimension, 'width'],
            source: [p.Instance, () => new ColumnDataSource()],
        });
        this.override({
            line_color: 'black',
        });
    }
}
SpanSet.__name__ = "SpanSet";
SpanSet.init_SpanSet();
//# sourceMappingURL=span_set.js.map