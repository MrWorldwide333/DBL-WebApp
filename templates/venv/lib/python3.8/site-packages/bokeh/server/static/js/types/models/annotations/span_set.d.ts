import { Annotation, AnnotationView } from "./annotation";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { LineScalar } from "../../core/property_mixins";
import { Line } from "../../core/visuals";
import { SpatialUnits, RenderMode, Dimension } from "../../core/enums";
import * as p from "../../core/properties";
import { Arrayable } from "../../core/types";
export declare class SpanSetView extends AnnotationView {
    model: SpanSet;
    visuals: SpanSet.Visuals;
    protected _location: Arrayable<number>;
    initialize(): void;
    connect_signals(): void;
    set_data(source: ColumnarDataSource): void;
    render(): void;
    protected _draw_span_set(i: number, loc: number): void;
}
export declare namespace SpanSet {
    type Attrs = p.AttrsOf<Props>;
    type Props = Annotation.Props & LineScalar & {
        render_mode: p.Property<RenderMode>;
        x_range_name: p.Property<string>;
        y_range_name: p.Property<string>;
        location: p.NumberSpec;
        location_units: p.Property<SpatialUnits>;
        dimension: p.Property<Dimension>;
        source: p.Property<ColumnarDataSource>;
    };
    type Visuals = Annotation.Visuals & {
        line: Line;
    };
}
export interface SpanSet extends SpanSet.Attrs {
}
export declare class SpanSet extends Annotation {
    properties: SpanSet.Props;
    constructor(attrs?: Partial<SpanSet.Attrs>);
    static init_SpanSet(): void;
}
